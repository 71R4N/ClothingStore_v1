import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # PostgreSQL
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "clothing_store")

    @property
    def POSTGRES_DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_POSTGRES_DB_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    REDIS_URL: str = os.getenv("REDIS_URL")

    # ML
    CATVTON_MODEL_PATH: str = os.getenv("CATVTON_MODEL_PATH", "/app/ml_models/catvton")

    TBANK_API_URL: str = os.getenv("TBANK_API_URL", "https://sandbox.tbank.ru/api")
    TBANK_MERCHANT_ID: str = os.getenv("TBANK_MERCHANT_ID", "")
    TBANK_SECRET_KEY: str = os.getenv("TBANK_SECRET_KEY", "")

    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

settings = Settings()
