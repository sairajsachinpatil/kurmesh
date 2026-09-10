import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    log_level: str
    cors_origins: list[str]
    auth_secret: str = ""

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            database_url=os.environ.get("DATABASE_URL", ""),
            redis_url=os.environ.get("REDIS_URL", ""),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            cors_origins=[item.strip() for item in os.environ.get("CORS_ORIGINS", "http://localhost").split(",")],
            auth_secret=os.environ.get("AUTH_SECRET", ""),
        )
