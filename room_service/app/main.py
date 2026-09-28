from fastapi import FastAPI

from app.core.config import settings
from app.controllers.room_controller import room_router
from app.core.exception_handlers import room_exception_handler
from app.core.exceptions import RoomException


def create_app() -> FastAPI: 
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0"
    )

    app.include_router(room_router)
    app.add_exception_handler(RoomException, room_exception_handler)
    return app

app = create_app()