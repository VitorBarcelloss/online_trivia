from fastapi import FastAPI

from app.core.config import settings
from app.controllers.user_controller import router as user_router
from app.controllers.auth_controller import router as auth_router
from app.core.exceptions import UserException
from app.core.exception_handlers import service_exception_handler, security_exception_handler

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0"
)

app.include_router(user_router)
app.include_router(auth_router)

app.add_exception_handler(
    UserException,
    service_exception_handler,
)
app.add_exception_handler(
    UserException,
    security_exception_handler,
)