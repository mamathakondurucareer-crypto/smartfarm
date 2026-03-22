"""Application configuration loaded from environment variables."""

import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ──
    app_name: str = "SmartFarm OS"
    app_version: str = "1.0.0"
    debug: bool = False

    # SECRET_KEY must be set in .env — never use the fallback in production.
    # Generate a strong key with: python -c "import secrets; print(secrets.token_hex(32))"
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 10080  # 7 days

    # ── CORS ──
    # Comma-separated list of allowed origins.  Empty string = deny all cross-origin requests.
    # MUST be set explicitly in production via ALLOWED_ORIGINS environment variable.
    # Example: "https://farm.example.com,https://app.example.com"
    allowed_origins: str = ""

    # ── Brute-force protection ──
    login_max_attempts: int = 5       # failed attempts before lockout
    login_lockout_seconds: int = 900  # 15-minute lockout

    # ── Database ──
    database_url: str = "sqlite:///./smartfarm.db"

    # ── AI ──
    anthropic_api_key: str = ""

    # ── Farm ──
    farm_name: str = "Nellore Integrated Smart Farm"
    farm_location: str = "Nellore District, Andhra Pradesh"
    farm_area_acres: float = 5.0
    farm_lat: float = 14.4426
    farm_lon: float = 79.9865

    # ── Alert Thresholds ──
    dissolved_oxygen_critical: float = 4.0
    dissolved_oxygen_warning: float = 4.5
    ammonia_critical: float = 0.05
    ph_min: float = 6.5
    ph_max: float = 8.5
    gh_temp_max: float = 38.0
    gh_humidity_max: float = 85.0
    poultry_ammonia_max: float = 20.0
    reservoir_low_pct: float = 25.0

    # ── Markets ──
    market_cities: str = "Hyderabad,Chennai,Vijayawada,Kadapa,Nellore"

    def effective_secret_key(self) -> str:
        """Return configured secret or raise on startup if missing in production."""
        if self.secret_key:
            return self.secret_key
        if self.debug:
            # Dev-only: generate a stable random key for the process lifetime.
            # Store it on the class so the same value is returned on every call.
            if not hasattr(Settings, "_dev_secret"):
                Settings._dev_secret = secrets.token_hex(32)
            return Settings._dev_secret
        raise RuntimeError(
            "SECRET_KEY must be set in .env for production. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
