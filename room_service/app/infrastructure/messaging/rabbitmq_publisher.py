import json

import aio_pika

from app.core.config import settings


EXCHANGE_NAME = "room_events"


async def publish_player_joined(
    room_code: str,
    player_id: str,
) -> None:
    connection = await aio_pika.connect_robust(
        settings.rabbitmq_url
    )

    try:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        event = {
            "type": "player_joined",
            "room_code": room_code,
            "player_id": player_id,
            "nickname": player_id,
        }

        message = aio_pika.Message(
            body=json.dumps(event).encode(),
            content_type="application/json",
        )

        await exchange.publish(
            message,
            routing_key="room.player.joined",
        )

    finally:
        await connection.close()


async def publish_player_left(
    room_code: str,
    player_id: str,
) -> None:
    connection = await aio_pika.connect_robust(
        settings.rabbitmq_url
    )

    try:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        event = {
            "type": "player_left",
            "room_code": room_code,
            "player_id": player_id,
        }

        message = aio_pika.Message(
            body=json.dumps(event).encode(),
            content_type="application/json",
        )

        await exchange.publish(
            message,
            routing_key="room.player.left",
        )

    finally:
        await connection.close()