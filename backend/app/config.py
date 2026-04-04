import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "ExamPulse API")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./exampulse.db")


settings = Settings()
