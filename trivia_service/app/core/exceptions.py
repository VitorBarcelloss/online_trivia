from typing import NamedTuple


class ErrorMessage(NamedTuple):
    status_code: int
    code: str
    message: str


class TriviaErrorMessages:
    QUESTION_NOT_FOUND = ErrorMessage(404, "QUESTION_NOT_FOUND", "Question not found.")
    QUESTIONS_NOT_FOUND = ErrorMessage(404, "QUESTIONS_NOT_FOUND", "No questions found.")
    QUESTION_CREATION_FAILED = ErrorMessage(500, "QUESTION_CREATION_FAILED", "Failed to create question.")
    PACKAGE_ID_MISSING = ErrorMessage(400, "PACKAGE_ID_MISSING", "Question package ID is required.")
    QUESTION_ID_MISSING = ErrorMessage(400, "QUESTION_ID_MISSING", "Question ID is required.")
    UNAUTHORIZED_PACKAGE_UPDATE = ErrorMessage(403, "UNAUTHORIZED_PACKAGE_UPDATE", "Only the package author can modify it.")
    UNAUTHORIZED_QUESTION_UPDATE = ErrorMessage(403, "UNAUTHORIZED_QUESTION_UPDATE", "Only the package author can modify its questions.")
    UNAUTHORIZED_ALTERNATIVE_UPDATE = ErrorMessage(403, "UNAUTHORIZED_ALTERNATIVE_UPDATE", "Only the package author can modify its alternatives.")
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