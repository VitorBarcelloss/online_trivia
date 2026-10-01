from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "trivia-service"
    debug: bool = False
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "trivia"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()