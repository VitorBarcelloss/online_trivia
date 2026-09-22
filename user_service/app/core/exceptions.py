from typing import NamedTuple

class ErrorMessage(NamedTuple):
    status_code: int
    code: str
    message: str
    
class SecurityErrorMessage:
    INVALID_JWT_TOKEN = ErrorMessage(
        status_code=401,
        code="INVALID_JWT_TOKEN",
        message="This jwt token is invalid, please check if it is corrupted.",
    )
    
    INVALID_USER_TOKEN = ErrorMessage(
        status_code=401,
        code="INVALID_USER_TOKEN",
        message="This user token is invalid or missing",
    )
    
class ServiceErrorMessage:
    INVALID_USER_TOKEN = ErrorMessage(
        status_code=401,
        code="INVALID_USER_TOKEN",
        message="This user token is invalid or missing",
    )
    
class UserException(Exception):
    def __init__(self, error: ErrorMessage):
        self.status_code = error.status_code
        self.code = error.code
        self.message = error.message
        
        super().__init__(error.message)