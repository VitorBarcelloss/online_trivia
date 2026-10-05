from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"

    room_service_url: str = (
        "http://room-service:8002/rooms"
    )

    trivia_service_url: str = (
        "http://trivia-service:8001/question-packages"
    )

    rabbitmq_url: str = (
        "amqp://guest:guest@rabbitmq:5672/"
    )

    game_ttl: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
