from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import TriviaException


async def trivia_exception_handler(
    _: Request,
    exception: TriviaException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={"code": exception.code, "message": exception.message},
    )