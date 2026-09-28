from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.controllers.room_controller import room_router
from app.core.exception_handlers import room_exception_handler
from app.core.exceptions import RoomException
from app.database.redis import close_redis_client, create_redis_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_client = create_redis_client()
    await redis_client.ping()
    try:
        yield
    finally:
        await close_redis_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(room_router)
    app.add_exception_handler(RoomException, room_exception_handler)
    return app


app = create_app()