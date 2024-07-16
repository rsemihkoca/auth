from abc import ABC, abstractmethod


class AbstractException(ABC, Exception):
    """ Abstract base class for custom exceptions """

    @abstractmethod
    def __init__(self, message: str, status_code: int, details: str):
        self.message = message
        self.status_code = status_code
        self.details = details


class ClientExistException(AbstractException):
    """ Exception raised when client already exists """

    def __init__(self):
        super().__init__(
            message="CLIENT_ALREADY_EXISTS",
            status_code=400,
            details="Client already exists, please use a different client ID"
        )


class ClientNotExistException(AbstractException):
    """ Exception raised when client does not exist """

    def __init__(self):
        super().__init__(
            message="CLIENT_NOT_FOUND",
            status_code=404,
            details="Client not found"
        )


class MQTTException(AbstractException):

    def __init__(self, message: str, status_code: int, detail: str):
        super().__init__(
            message=message,
            status_code=status_code,
            details=detail
        )
