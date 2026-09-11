import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    log_level: str
    cors_origins: list[str]
    auth_secret: str = ""

    def validate(self) -> None:
        """Validate secrets needed by the authenticated application API.

        Database and Redis availability remains observable through health checks;
        a signing key is different because operating without one makes auth unsafe.
        """
        if len(self.auth_secret) < 32 or self.auth_secret.startswith("replace-with-"):
            raise ValueError("AUTH_SECRET must be configured with at least 32 characters")

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            database_url=os.environ.get("DATABASE_URL", ""),
            redis_url=os.environ.get("REDIS_URL", ""),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            cors_origins=[item.strip() for item in os.environ.get("CORS_ORIGINS", "http://localhost").split(",")],
            auth_secret=os.environ.get("AUTH_SECRET", ""),
        )
