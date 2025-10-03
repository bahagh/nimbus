from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    # Read env from the API .env; ignore all unrelated keys (jwt, cors, etc.)
    model_config = SettingsConfigDict(env_file="../api/.env", extra="ignore")

settings = Settings()
