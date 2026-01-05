from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_token: str
    database: str = "sqlite:///./bat.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()