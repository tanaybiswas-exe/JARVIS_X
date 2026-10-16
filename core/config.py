from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    JARVIS_AI_PROVIDER: str = "openai"
    JARVIS_AI_MODEL: str = "gpt-4o"
    JARVIS_AI_API_KEY: str = ""
    JARVIS_AI_API_BASE: str = "https://api.openai.com/v1"
    JARVIS_ALLOWED_WORKSPACE: str = "./workspace"
    JARVIS_PERMISSION_LEVEL: str = "CONFIRM"
    JARVIS_HOST: str = "127.0.0.1"
    JARVIS_PORT: int = 8000
    JARVIS_CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
WORKSPACE_PATH = Path(settings.JARVIS_ALLOWED_WORKSPACE).resolve()
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)