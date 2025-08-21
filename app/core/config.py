import os
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    env: str = os.getenv("ENV", "dev")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    allow_writes: bool = os.getenv("ALLOW_WRITES", "false").lower() == "true"
    backup_verified: bool = os.getenv("BACKUP_VERIFIED", "false").lower() == "true"

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
