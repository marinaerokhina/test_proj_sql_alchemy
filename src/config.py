"""Validated PostgreSQL connection settings from an untracked local .env file."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str
    DB_NAME: str = "sqlalchemy_practice"

    @property
    def DATABASE_URL_asyncpg(self) -> URL:
        return URL.create(
            "postgresql+asyncpg",
            username=self.DB_USER, password=self.DB_PASS,
            host=self.DB_HOST, port=self.DB_PORT, database=self.DB_NAME,
        )

    @property
    def DATABASE_URL_psycopg(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.DB_USER, password=self.DB_PASS,
            host=self.DB_HOST, port=self.DB_PORT, database=self.DB_NAME,
        )

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
