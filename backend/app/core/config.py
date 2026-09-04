import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "BugForge"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///./bugforge.db"
    
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.5-flash"
    
    RUNTIME_TIMEOUT: int = 30
    PYTHON_EXECUTABLE: str = "python"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
