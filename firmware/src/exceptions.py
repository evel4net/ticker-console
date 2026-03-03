class InvalidCredentials(Exception):
    pass

class InvalidSessionID(Exception):
    pass

class InvalidToken(Exception):
    pass

class ExpiredToken(Exception):
    pass

class DecryptionError(Exception):
    pass

class ServerKeypairNotFound(Exception):
    pass

class InvalidRoute(Exception):
    pass

class BadRequest(Exception):
    pass

class NotFound(Exception):
    pass

class AlreadyExists(Exception):
    pass

class InvalidArguments(Exception):
    pass