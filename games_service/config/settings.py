from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"

    room_service_url: str = "http://room-service:8000/rooms"

    trivia_service_url: str = (
        "http://trivia-service:8000/packages"
    )

    rabbitmq_url: str = (
        "amqp://guest:guest@rabbitmq:5672/"
    )

    game_ttl: int = 3600


settings = Settings()