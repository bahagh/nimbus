from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    app_name: str = "Nimbus API"
    api_v1_prefix: str = "/v1"

    # JWT
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_seconds: int = 3600
    jwt_refresh_ttl_seconds: int = 60 * 60 * 24 * 7  # 7 days

    # Ingest HMAC (demo/global; move per-project later)
    ingest_api_key_id: str = "local-key-id"
    ingest_api_key_secret: str = "local-super-secret"

    # DB
    database_url: AnyUrl | str = "postgresql+asyncpg://postgres:baha123@localhost:5432/nimbus"

    class Config:
        env_prefix = "NIMBUS_"
        case_sensitive = False

settings = Settings()
