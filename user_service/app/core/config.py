from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str
    debug: bool = False
    
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_password: str
    postgres_user: str
    
    jwt_secret:str
    
    @property
    def database_url(self) -> str:
        return(
            f"postgresql+psycopg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
settings = Settings()