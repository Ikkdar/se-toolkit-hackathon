import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "ExamPulse API")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./exampulse.db")
    llm_provider: str = os.getenv("LLM_PROVIDER", "auto")
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "12"))

    qwen_proxy_base_url: str = os.getenv("QWEN_PROXY_BASE_URL", "http://localhost:8080/v1")
    qwen_proxy_api_key: str = os.getenv("QWEN_PROXY_API_KEY", "fake-key")
    qwen_proxy_model: str = os.getenv("QWEN_PROXY_MODEL", "coder-model")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))


settings = Settings()
