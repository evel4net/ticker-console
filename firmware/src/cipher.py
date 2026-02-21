import hashlib
import json
import uos
import ucryptolib

import dependencies.ecc_pycrypto as ecc
import dependencies.hmac as hmac
from src.session_manager import UnauthorizedAccessException

class Cipher(object):
    def __init__(self, priv_key_path: str, pub_key_path: str):
        self.__curve = ecc.P256

        self.__private_key, self.__public_key = self.load_keypair(priv_key_path, pub_key_path)

        self.__aes_keys = {} # session_id: aes key

        self.__current_session_id = 1

    def load_keypair(self, priv_key_path: str, pub_key_path: str) -> (int, ecc.Point):
        try:
            with open(priv_key_path, "r") as f:
                priv_hex = f.read()

            with open(pub_key_path, "r") as f:
                pub_hex = f.read()

            priv = int(priv_hex, 16)
            pub = self.get_public_key_point(pub_hex)

            return priv, pub
        except Exception as e:
            raise Exception(f"Private-public keypair not found. {e}")

    def login_client(self, client_pub: str) -> str:
        session_id = str(self.__current_session_id)
        self.__current_session_id += 1

        client_aes_key = self.get_aes_key(client_pub)

        self.__aes_keys[session_id] = client_aes_key
        print(self.__aes_keys)

        return session_id

    def signout_client(self, session_id: str) -> bytes:
        return self.__aes_keys.pop(session_id)

    def get_public_key_point(self, pub_hex: str) -> ecc.AffinePoint:
        pub_hex = pub_hex[2:]
        pub_x = pub_hex[:64]
        pub_y = pub_hex[64:]

        return ecc.AffinePoint(self.__curve, int(pub_x, 16), int(pub_y, 16))

    def get_shared_secret(self, other_pub_hex: str) -> int:
        other_public_key = self.get_public_key_point(other_pub_hex)

        shared_point = ecc.ecdh_shared(self.__private_key, other_public_key)

        return shared_point.x

    def get_aes_key(self, other_pub_hex: str) -> bytes:
        shared_secret = self.get_shared_secret(other_pub_hex)

        return hashlib.sha256(shared_secret.to_bytes(32, "big")).digest()

    """ AES ENCRYPTION / DECRYPTION """

    def aes_ctr_mode(self, aes_key: bytes, iv: bytes, text: bytes) -> bytes:
        cipher = ucryptolib.aes(aes_key, 1) # ECB mode
        counter = int.from_bytes(iv, "big")

        out = bytearray()

        for i in range(0, len(text), 16):
            block = text[i:i + 16]
            keystream = cipher.encrypt(counter.to_bytes(16, "big"))
            out_block = bytes(a ^ b for a,b in zip(block, keystream))
            out.extend(out_block)
            counter = (counter + 1) & ((1 << 128) - 1)

        return bytes(out)

    def encrypt_text(self, aes_key: bytes, plain_text: bytes) -> (bytes, bytes, bytes):
        iv = uos.urandom(16) # counter block
        cipher_text = self.aes_ctr_mode(aes_key, iv, plain_text)

        hmac_tag = hmac.new(aes_key, iv + cipher_text, hashlib.sha256).digest()

        return iv, cipher_text, hmac_tag

    def decrypt_text(self, aes_key: bytes, iv: bytes, cipher_text: bytes, hmac_tag: bytes) -> bytes:
        hmac_expected = hmac.new(aes_key, iv + cipher_text, hashlib.sha256).digest()

        if hmac_expected != hmac_tag:
            raise UnauthorizedAccessException("HMAC tag not corresponding.")

        plain_text = self.aes_ctr_mode(aes_key, iv, cipher_text)

        return plain_text

    def encrypt_response(self, response: dict, session_id: str, is_signout_response: bool = False) -> dict:
        response_str = json.dumps(response)
        aes_iv, cipher_text, hmac_tag = self.encrypt_text(self.__aes_keys[session_id], response_str.encode())

        response_json = {"cipher_text": cipher_text.hex(), "iv": aes_iv.hex(), "tag": hmac_tag.hex()}

        if is_signout_response:
            self.signout_client(session_id)

        return response_json

    def decrypt_request(self, request_body: dict, session_id: str, is_login_request: bool = False) -> (dict, str):
        if is_login_request:
            client_public_key = request_body["client_pub"]
            session_id = self.login_client(client_public_key)

        cipher_text = bytes.fromhex(request_body["cipher_text"])
        aes_iv = bytes.fromhex(request_body["iv"])
        hmac_tag = bytes.fromhex(request_body["tag"])

        plain_text = self.decrypt_text(self.__aes_keys[session_id], aes_iv, cipher_text, hmac_tag)

        return json.loads(plain_text.decode()), session_id