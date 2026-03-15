"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ──
    app_name: str = "SmartFarm OS"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
