from typing import NamedTuple


class ErrorMessage(NamedTuple):
    status_code: int
    code: str
    message: str


class RoomErrorMessage:
    IDEMPOTENCY_KEY_CONFLICT = ErrorMessage(
        status_code=409,
        code="IDEMPOTENCY_KEY_CONFLICT",
        message="This idempotency key is already in use for a different or pending request.",
    )
    INVALID_REQUEST = ErrorMessage(
        status_code=422,
        code="INVALID_REQUEST",
        message="One or more provided fields are invalid."
    )
    ROOM_NOT_FOUND = ErrorMessage(
        status_code=404,
        code="ROOM_NOT_FOUND",
        message="Room was not found.",
    )
    PLAYER_NOT_IN_ROOM = ErrorMessage(
        status_code=404,
        code="PLAYER_NOT_IN_ROOM",
        message="Player is not in this room.",
    )
    ROOM_FULL = ErrorMessage(
        status_code=409,
        code="ROOM_FULL",
        message="Room has reached its player limit.",
    )
    ROOM_NOT_WAITING = ErrorMessage(
        status_code=409,
        code="ROOM_NOT_WAITING",
        message="Room is not accepting this operation in its current state.",
    )
    ROOM_ALREADY_STARTED = ErrorMessage(
        status_code=409,
        code="ROOM_ALREADY_STARTED",
        message="The room has already started or finished.",
    )
    NOT_ENOUGH_PLAYERS = ErrorMessage(
        status_code=409,
        code="NOT_ENOUGH_PLAYERS",
        message="At least one player is required to start the game.",
    )
    HOST_ONLY = ErrorMessage(
        status_code=403,
        code="HOST_ONLY",
        message="Only the room host can perform this operation.",
    )
    PRIVATE_ROOM_CODE_REQUIRED = ErrorMessage(
        status_code=403,
        code="PRIVATE_ROOM_CODE_REQUIRED",
        message="A valid room code is required to join a private room.",
    )
    ROOM_CODE_GENERATION_FAILED = ErrorMessage(
        status_code=503,
        code="ROOM_CODE_GENERATION_FAILED",
        message="Could not generate a unique room code. Try again.",
    )
    ROOM_UPDATE_CONFLICT = ErrorMessage(
        status_code=409,
        code="ROOM_UPDATE_CONFLICT",
        message="Room changed during the request. Please retry.",
    )
    HOST_ID_REQUIRED = ErrorMessage(
        status_code=400,
        code="HOST_ID_REQUIRED",
        message="Host ID is required to create a room.",
    )
    ROOM_PLAYER_LIMIT_EXCEEDED = ErrorMessage(
        status_code=400,
        code="ROOM_PLAYER_LIMIT_EXCEEDED",
        message="The number of players in the room exceeds the maximum allowed.",
    )
    PRIVATE_ROOM_REQUIRED_PASSWORD = ErrorMessage(
        status_code=400,
        code="PRIVATE_ROOM_REQUIRED_PASSWORD",
        message="A password is required to join a private room.",
    )
    PLAYER_ALREADY_IN_ROOM = ErrorMessage(
        status_code=409,
        code="PLAYER_ALREADY_IN_ROOM",
        message="Player is already in this room.",
    )
    ROOM_UPDATE_FAILED = ErrorMessage(
        status_code=503,
        code="ROOM_UPDATE_FAILED",
        message="This room couldn't be updated, please check if it is still a valid room."        
    )

class RoomException(Exception):
    def __init__(self, error: ErrorMessage):
        self.status_code = error.status_code
        self.code = error.code
        self.message = error.message
        super().__init__(error.message)