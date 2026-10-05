from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "room-service"
    debug: bool = False

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    rabbitmq_url: str = (
        "amqp://guest:guest@rabbitmq:5672/"
    )

    game_service_url: str = (
        "http://game-service:8003/games"
    )

    room_code_length: int = 6
    room_code_alphabet: str = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    room_ttl: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()