from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "scraPy API"
    API_V1_STR: str = "/api/v1"
    
    # Database - will use Railway's DATABASE_URL in production, local postgres in dev
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "advait"
    POSTGRES_PASSWORD: str = "advait"
    POSTGRES_DB: str = "scrapeflow"
    DATABASE_URL: Optional[str] = None  # Railway will set this automatically

    # Redis - will use Railway's REDIS_URL in production, local redis in dev
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None  # Railway will set this automatically
    
    # LLM
    GEMINI_API_KEY: Optional[str] = None

    # CORS - frontend URL, defaults to localhost for dev
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        case_sensitive = True
        env_file = ".env"
    
    @property
    def async_database_url(self) -> str:
        """Return the full database URL, using Railway's if available, otherwise construct from parts"""
        if self.DATABASE_URL:
            # Railway provides postgres:// but we need postgresql+asyncpg://
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    @property
    def redis_connection_url(self) -> str:
        """Return Redis URL, using Railway's if available, otherwise construct from host/port"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

settings = Settings()
