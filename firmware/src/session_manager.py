import utime

from src.config_private import USERS
from src.constants import TOKEN_LIFETIME
from src.utilities import generate_random_128_bits


class UnauthorizedAccessException(Exception):
    def __init__(self, msg):
        super().__init__(f"Unauthorized access. {msg}")


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

        raise UnauthorizedAccessException("Invalid username or password.")

    def validate_token(self, token: str):
        if token not in self.__tokens.keys():
            raise UnauthorizedAccessException("Invalid token.")

        if utime.time() - self.__tokens[token] > TOKEN_LIFETIME:
            self.__tokens.pop(token)
            raise UnauthorizedAccessException("Expired token.")

    def rotate_token(self, old_token) -> str:
        self.validate_token(old_token)

        self.__tokens.pop(old_token)

        token = self.__generate_token()

        return token