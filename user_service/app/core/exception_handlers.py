from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import UserException

async def service_exception_handler(
    request: Request,
    exception: UserException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "status": exception.status_code,
            "error": exception.code,
            "message": exception.message,
        },
    )

async def security_exception_handler(
    request: Request,
    exception: UserException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "status": exception.status_code,
            "error": exception.code,
            "message": exception.message,
        },
    )
