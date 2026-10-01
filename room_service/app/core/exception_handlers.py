from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import RoomException


async def room_exception_handler(
    _: Request,
    exception: RoomException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "status": exception.status_code,
            "code": exception.code,
            "message": exception.message,
        },
    )