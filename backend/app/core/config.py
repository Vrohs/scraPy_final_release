from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ScrapeFlow API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "advait"
    POSTGRES_PASSWORD: str = "advait"
    POSTGRES_DB: str = "scrapeflow"
    DATABASE_URL: Optional[str] = "postgresql+asyncpg://advait:advait@localhost/scrapeflow"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # LLM
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
