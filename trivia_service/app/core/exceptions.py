from typing import NamedTuple


class ErrorMessage(NamedTuple):
    status_code: int
    code: str
    message: str


class TriviaErrorMessages:
    DUPLICATE_RESOURCE_CONFLICT = ErrorMessage(
        status_code=409,
        code="DUPLICATE_RESOURCE_CONFLICT",
        message="A resource with this natural key already exists with different data."
    )
    INVALID_REQUEST = ErrorMessage(
        status_code=422,
        code="INVALID_REQUEST",
        message="One or more provided fields are invalid."
    )
    QUESTION_NOT_FOUND = ErrorMessage(
        status_code=404,
        code="QUESTION_NOT_FOUND",
        message="Question not found."
    )
    QUESTIONS_NOT_FOUND = ErrorMessage(
        status_code=404,
        code="QUESTIONS_NOT_FOUND",
        message="No questions found."
    )
    QUESTION_CREATION_FAILED = ErrorMessage(
        status_code=500,
        code="QUESTION_CREATION_FAILED",
        message="Failed to create question."
    )
    PACKAGE_ID_MISSING = ErrorMessage(
        status_code=400,
        code="PACKAGE_ID_MISSING",
        message="Question package ID is required."
    )
    QUESTION_ID_MISSING = ErrorMessage(
        status_code=400,
        code="QUESTION_ID_MISSING",
        message="Question ID is required."
    )
    UNAUTHORIZED_PACKAGE_UPDATE = ErrorMessage(
        status_code=403,
        code="UNAUTHORIZED_PACKAGE_UPDATE",
        message="Only the package author can modify it."
    )
    UNAUTHORIZED_QUESTION_UPDATE = ErrorMessage(
        status_code=403,
        code="UNAUTHORIZED_QUESTION_UPDATE",
        message="Only the package author can modify its questions."
    )
    UNAUTHORIZED_ALTERNATIVE_UPDATE = ErrorMessage(
        status_code=403,
        code="UNAUTHORIZED_ALTERNATIVE_UPDATE",
        message="Only the package author can modify its alternatives."
    )
    ALTERNATIVE_NOT_FOUND = ErrorMessage(
        status_code=404,
        code="ALTERNATIVE_NOT_FOUND",
        message="Alternative not found.",
    )
    ALTERNATIVE_CREATION_FAILED = ErrorMessage(
        status_code=500,
        code="ALTERNATIVE_CREATION_FAILED",
        message="Failed to create alternative.",
    )
    ALTERNATIVE_UPDATE_FAILED = ErrorMessage(
        status_code=500,
        code="ALTERNATIVE_UPDATE_FAILED",
        message="Failed to update alternative.",
    )
    ALTERNATIVE_DELETE_FAILED = ErrorMessage(
        status_code=500,
        code="ALTERNATIVE_DELETE_FAILED",
        message="Failed to delete alternative.",
    )
    PACKAGE_NOT_FOUND = ErrorMessage(
        status_code=404,
        code="PACKAGE_NOT_FOUND",
        message="Question package not found.",
    )
    PACKAGE_CREATION_FAILED = ErrorMessage(
        status_code=500,
        code="PACKAGE_CREATION_FAILED",
        message="Failed to create question package.",
    )


class TriviaException(Exception):
    def __init__(self, error: ErrorMessage):
        self.status_code = error.status_code
        self.code = error.code
        self.message = error.message
        super().__init__(error.message)