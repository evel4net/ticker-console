from src.config_private import USERS

class UnauthorizedAccessException(Exception):
    def __init__(self, msg):
        super().__init__(f"Unauthorized access. {msg}")

class SessionManager:
    def __init__(self):
        self.__tokens = []
        self.__i = 0

    def create_session(self, username, password) -> str:
        if username in USERS and password == USERS[username]:
            token = self.__generate_token()
            self.__tokens.append(token)

            return token

        raise UnauthorizedAccessException("Invalid username or password.")

    def validate_token(self, token: str):
        if token not in self.__tokens:
            raise UnauthorizedAccessException("Invalid token.")

        if self.__is_expired(token):
            raise UnauthorizedAccessException("Expired token.")

    def rotate_token(self, old_token) -> str:
        if self.__is_expired(old_token):
            raise UnauthorizedAccessException("Expired token.")

        self.__tokens.remove(old_token)

        token = self.__generate_token()
        self.__tokens.append(token)

        return token

    def __generate_token(self): # TODO generate a token which includes expiration datetime
        self.__i += 1
        return str(self.__i)

    def __is_expired(self, token):
        if token not in self.__tokens:
            raise UnauthorizedAccessException("Invalid token.")

        # return True  TODO check if token expired, remove if it expired

        return False