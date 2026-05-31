from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://discoveryfx:discoveryfx@postgres:5432/discoveryfx"
    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24
    refresh_token_days: int = 30

    ebay_env: str = "sandbox"            # "sandbox" | "prod"
    ebay_client_id: str = ""
    ebay_client_secret: str = ""
    ebay_redirect_uri: str = "http://localhost:8081/api/stores/ebay/callback"

    anthropic_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
