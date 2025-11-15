from typing import List, Literal
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, Field, SecretStr

class Settings(BaseSettings):
    # App Configuration
    app_name: str = "Nimbus API"
    api_v1_prefix: str = "/v1"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = Field(default=False, description="Enable debug mode")

    # Security - JWT
    jwt_secret: SecretStr = Field(default="change-me-local-test-secret-key-32chars", description="JWT signing secret", min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_alg: str = Field(default="HS256", description="JWT algorithm (alias for jwt_algorithm)")
    jwt_access_ttl_seconds: int = 3600
    jwt_refresh_ttl_seconds: int = 60 * 60 * 24 * 7  # 7 days

    # Security - OIDC (Optional)
    oidc_issuer: str | None = Field(default=None, description="OIDC issuer URL")
    oidc_audience: str | None = Field(default=None, description="OIDC audience")

    # Security - API Keys (DEPRECATED: move to per-project)
    ingest_api_key_id: str = Field(default="local-key-id", description="Global API key ID (deprecated)")
    ingest_api_key_secret: SecretStr = Field(default="local-super-secret", description="Global API secret (deprecated)")

    # Database Configuration
    database_url: AnyUrl | str = Field(default="sqlite+aiosqlite:///:memory:", description="Database connection URL")
    db_pool_size: int = Field(default=10, ge=1, le=50)
    db_max_overflow: int = Field(default=20, ge=0, le=100)
    db_pool_timeout: int = Field(default=30, ge=1)

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_pool_size: int = Field(default=10, ge=1, le=50)

    # Security Configuration
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost", "http://localhost:5173"], description="CORS allowed origins")
    def __init__(self, **values):
        super().__init__(**values)
        # If allowed_origins is a string, parse it as a list
        if isinstance(self.allowed_origins, str):
            import json
            try:
                self.allowed_origins = json.loads(self.allowed_origins)
            except Exception:
                self.allowed_origins = [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=10000, ge=1, le=100000)
    
    # Monitoring and Observability
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    enable_tracing: bool = Field(default=False, description="Enable OpenTelemetry tracing")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Feature Flags
    enable_websockets: bool = Field(default=True, description="Enable WebSocket support")
    enable_batch_processing: bool = Field(default=True, description="Enable batch event processing")

    class Config:
        env_prefix = "NIMBUS_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_database_url(self) -> str:
        """Get database URL as string for SQLAlchemy"""
        return str(self.database_url)

    def get_jwt_secret(self) -> str:
        """Get JWT secret as string"""
        return self.jwt_secret.get_secret_value()

    def get_ingest_secret(self) -> str:
        """Get ingest API secret as string"""
        return self.ingest_api_key_secret.get_secret_value()

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"

settings = Settings()
