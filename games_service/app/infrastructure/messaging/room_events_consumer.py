import json

import aio_pika

from app.presentation.game_dependencies import (
    add_player_use_case,
    connection_manager,
    game_repository,
    remove_player_use_case,
)
from app.presentation.game_runtime import (
    build_ranking,
)


RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"

EXCHANGE_NAME = "room_events"

QUEUE_NAME = "game_service_room_events"


async def handle_event(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process():
        data = json.loads(
            message.body.decode()
        )

        event_type = data.get("type")
        room_code = data.get("room_code")

        if not room_code:
            return

        game_id = connection_manager.get_game_id(
            room_code,
        )

        if not game_id:
            return

        if event_type == "player_joined":
            player_id = data.get("player_id")
            nickname = data.get("nickname")

            if not player_id or not nickname:
                return

            game = await add_player_use_case.execute(
                game_id=game_id,
                player_id=player_id,
                nickname=nickname,
            )

            await connection_manager.broadcast(
                game_id=game_id,
                message={
                    "type": "player_joined",
                    "player": {
                        "user_id": player_id,
                        "nickname": nickname,
                        "score": 0,
                    },
                },
            )

            await connection_manager.broadcast(
                game_id=game_id,
                message={
                    "type": "ranking_updated",
                    "ranking": build_ranking(game),
                },
            )

        elif event_type == "player_left":
            player_id = data.get("player_id")

            if not player_id:
                return

            await remove_player_use_case.execute(
                game_id=game_id,
                player_id=player_id,
            )

            await connection_manager.broadcast(
                game_id=game_id,
                message={
                    "type": "player_left",
                    "player_id": player_id,
                },
            )

            game = await game_repository.get(
                game_id,
            )

            if game:
                await connection_manager.broadcast(
                    game_id=game_id,
                    message={
                        "type": "ranking_updated",
                        "ranking": build_ranking(game),
                    },
                )


async def start_room_events_consumer() -> None:
    connection = await aio_pika.connect_robust(
        RABBITMQ_URL,
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )

    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True,
    )

    await queue.bind(
        exchange,
        routing_key="room.player.*",
    )

    await queue.consume(
        handle_event,
    )