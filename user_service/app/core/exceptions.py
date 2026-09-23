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
    
    INVALID_PASSWORD_PATTERN = ErrorMessage(
        status_code=400,
        code="INVALID_PASSWORD_PATTERN",
        message="Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.",
    )
    
    USER_CREATION_FAILED = ErrorMessage(
        status_code=500,
        code="USER_CREATION_FAILED",
        message="User creation failed, please try again later.",
    )
    
    INVALID_USERNAME = ErrorMessage(
        status_code=401,
        code="INVALID_USERNAME",
        message="Invalid username, please check if the username is correct.",
    )
    
    INVALID_PASSWORD = ErrorMessage(
        status_code=401,
        code="INVALID_PASSWORD",
        message="Invalid password, please check if the password is correct.",
    )

class UserException(Exception):
    def __init__(self, error: ErrorMessage):
        self.status_code = error.status_code
        self.code = error.code
        self.message = error.message
        
        super().__init__(error.message)