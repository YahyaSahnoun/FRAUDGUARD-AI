"""Centralized application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    kafka_bootstrap_servers: str = "localhost:9092"

    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    postgres_db: str = "fraudguard"
    postgres_user: str = "fraudguard"
    postgres_password: SecretStr = SecretStr("")

    minio_endpoint: str = "localhost:9000"
    minio_access_key: SecretStr = SecretStr("")
    minio_secret_key: SecretStr = SecretStr("")

    llm_provider: Literal["mock", "groq"] = "mock"
    groq_api_key: SecretStr = SecretStr("")

    def model_post_init(self, __context: object) -> None:
        if self.app_env == "production":
            if not self.postgres_password.get_secret_value():
                raise ValueError("POSTGRES_PASSWORD required in production")

            if not self.minio_access_key.get_secret_value():
                raise ValueError("MINIO_ACCESS_KEY required in production")

            if not self.minio_secret_key.get_secret_value():
                raise ValueError("MINIO_SECRET_KEY required in production")

        if self.llm_provider == "groq" and not self.groq_api_key.get_secret_value():
            raise ValueError("GROQ_API_KEY required when LLM_PROVIDER=groq")


@lru_cache
def get_settings() -> Settings:
    return Settings()
