from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    CORE_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "dev"
    FRONTEND_URL: str = "http://localhost:3000"
    AUTH_ENABLED: bool = False
    CORE_JWT_SECRET: str | None = None
    CORE_JWT_ALG: str = "HS256"
    CORE_JWT_ISSUER: str | None = "core"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
