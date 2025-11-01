from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "Nimbus API"
    
    # DB / cache
    database_url: str = "sqlite+aiosqlite:///:memory:"  # overridden by .env in real use
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-me-local"
    jwt_alg: str = "HS256"

    # Ingest HMAC
    ingest_api_key_id: str = "local-key-id"
    ingest_api_key_secret: str = "local-super-secret"

    # Optional OIDC (leave empty in dev/tests)
    oidc_issuer: str | None = None
    oidc_audience: str | None = None

    # API
    rate_limit_per_minute: int = 120
    cors_origins: list[str] = []

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
