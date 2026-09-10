from flask import Flask
from flask_cors import CORS

from app.api.v1.health import health_blueprint
from app.config import Settings
from app.logging import configure_logging


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or Settings.from_environment()
    configure_logging(settings.log_level)
    app = Flask(__name__)
    app.config["KURMESH_SETTINGS"] = settings
    CORS(app, resources={r"/api/*": {"origins": settings.cors_origins}})
    app.register_blueprint(health_blueprint, url_prefix="/api/v1/health")

    @app.get("/api/v1")
    def api_root() -> dict[str, str]:
        return {"service": "kurmesh-api", "version": "v1", "status": "INFRASTRUCTURE_ONLY"}

    return app
