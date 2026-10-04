from contextlib import asynccontextmanager

import asyncio

from fastapi import FastAPI

from app.infrastructure.messaging.room_events_consumer import (
    start_room_events_consumer,
)

from app.presentation.http.game_router import (
    router as game_router,
)

from app.presentation.websocket.game_websocket import (
    router as game_websocket_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit_task = asyncio.create_task(
        start_room_events_consumer()
    )

    yield

    rabbit_task.cancel()

    try:
        await rabbit_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Trivia Game Service",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(
    game_router,
    prefix="/games",
)

app.include_router(
    game_websocket_router,
    prefix="/games",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
    }