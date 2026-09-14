import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ProviderConfiguration:
    """Non-provider-specific configuration supplied to a future adapter."""

    name: str
    enabled: bool
    endpoint: str | None
    api_key: str | None
    timeout_seconds: int


@dataclass(frozen=True)
class Settings:
    database_url: str
    redis_url: str
    log_level: str
    cors_origins: list[str]
    auth_secret: str = ""
    environment_providers: tuple[ProviderConfiguration, ...] = ()

    def validate(self) -> None:
        """Validate secrets needed by the authenticated application API.

        Database and Redis availability remains observable through health checks;
        a signing key is different because operating without one makes auth unsafe.
        """
        if len(self.auth_secret) < 32 or self.auth_secret.startswith("replace-with-"):
            raise ValueError("AUTH_SECRET must be configured with at least 32 characters")
        for provider in self.environment_providers:
            if not provider.name.replace("_", "").replace("-", "").isalnum():
                raise ValueError("Environment provider names may contain only letters, numbers, hyphens, and underscores")
            if provider.timeout_seconds < 1:
                raise ValueError("Environment provider timeout must be at least one second")
            if provider.enabled and not provider.endpoint:
                raise ValueError(f"Enabled environment provider {provider.name!r} requires an endpoint")
            if provider.endpoint:
                parsed = urlparse(provider.endpoint)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError(f"Environment provider {provider.name!r} endpoint must be an absolute HTTP(S) URL")

    def provider_configuration(self, name: str) -> ProviderConfiguration | None:
        return next((provider for provider in self.environment_providers if provider.name == name), None)

    @classmethod
    def from_environment(cls) -> "Settings":
        provider_names = tuple(item.strip() for item in os.environ.get("KURMESH_ENVIRONMENT_PROVIDERS", "").split(",") if item.strip())
        default_timeout = int(os.environ.get("KURMESH_ENVIRONMENT_PROVIDER_TIMEOUT_SECONDS", "15"))
        providers = tuple(
            ProviderConfiguration(
                name=name,
                enabled=os.environ.get(f"KURMESH_ENVIRONMENT_PROVIDER_{name.upper().replace('-', '_')}_ENABLED", "false").lower() == "true",
                endpoint=os.environ.get(f"KURMESH_ENVIRONMENT_PROVIDER_{name.upper().replace('-', '_')}_ENDPOINT") or None,
                api_key=os.environ.get(f"KURMESH_ENVIRONMENT_PROVIDER_{name.upper().replace('-', '_')}_API_KEY") or None,
                timeout_seconds=int(os.environ.get(f"KURMESH_ENVIRONMENT_PROVIDER_{name.upper().replace('-', '_')}_TIMEOUT_SECONDS", str(default_timeout))),
            )
            for name in provider_names
        )
        return cls(
            database_url=os.environ.get("DATABASE_URL", ""),
            redis_url=os.environ.get("REDIS_URL", ""),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            cors_origins=[item.strip() for item in os.environ.get("CORS_ORIGINS", "http://localhost").split(",")],
            auth_secret=os.environ.get("AUTH_SECRET", ""),
            environment_providers=providers,
        )
