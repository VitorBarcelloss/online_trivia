from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	app_name: str
	debug: bool
	redis_url: str
	jwt_secret: str


settings: Settings
