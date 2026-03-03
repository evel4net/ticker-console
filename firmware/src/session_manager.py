import utime

from src.config_private import USERS
from src.constants import TOKEN_LIFETIME
from src.utilities import generate_random_128_bits
from src.exceptions import InvalidCredentials, InvalidToken, ExpiredToken

class SessionManager:
    def __init__(self):
        self.__tokens = {} # token: created_at

    def __generate_token(self) -> str:
        token = generate_random_128_bits().hex()
        self.__tokens[token] = utime.time()

        return token

    def create_session(self, username, password) -> str:
        if username in USERS and password == USERS[username]:
            token = self.__generate_token()

            return token

        raise InvalidCredentials("Invalid username or password.")

    def validate_token(self, token: str):
        if token not in self.__tokens.keys():
            raise InvalidToken("Token not found.")

        if utime.time() - self.__tokens[token] > TOKEN_LIFETIME:
            self.__tokens.pop(token)
            raise ExpiredToken("Token expired.")

    def rotate_token(self, old_token) -> str:
        self.__tokens.pop(old_token)

        token = self.__generate_token()

        return token