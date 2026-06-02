from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "clothing_store"

    @property
    def POSTGRES_DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_POSTGRES_DB_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    RECAPTCHA_SITE_KEY: str = ""
    RECAPTCHA_SECRET_KEY: str = ""

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    REDIS_URL: str = "redis://localhost:6379/0"

    # CatVTON
    CATVTON_API_URL: str = "http://localhost:8001"
    CATVTON_TIMEOUT: int = 300
    CATVTON_ENABLED: bool = False
    CATVTON_FALLBACK_IMAGE: str = "/static/images/tryon_fallback.png"

    TBANK_API_URL: str = "https://sandbox.tbank.ru/api"
    TBANK_MERCHANT_ID: str = ""
    TBANK_SECRET_KEY: str = ""

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:8000"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
