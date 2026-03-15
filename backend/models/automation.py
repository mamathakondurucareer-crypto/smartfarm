"""Automation rules engine, execution logs, and drone flight management."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin, SoftDeleteMixin


class AutomationRule(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "automation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system: Mapped[str] = mapped_column(String(30), nullable=False)
    # Systems: irrigation, aeration, fish_feeder, egg_belt, manure_scraper, gh_climate, lighting, drone
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False)  # sensor, schedule, manual
    trigger_condition: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON: {"sensor": "soil_moisture", "operator": "<", "value": 35, "zone": "gh1"}
    # or: {"schedule": "06:00,12:00,17:00", "days": "daily"}
    action: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON: {"type": "relay", "device": "valve_zone1", "command": "on", "duration_min": 30}
    priority: Mapped[int] = mapped_column(Integer, default=5)  # 1=highest
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=15)
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class AutomationLog(Base, TimestampMixin):
    __tablename__ = "automation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("automation_rules.id"), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    trigger_value: Mapped[Optional[float]] = mapped_column(Float)
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # success, failure, timeout, overridden
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    manual_override: Mapped[bool] = mapped_column(Boolean, default=False)
    overridden_by: Mapped[Optional[str]] = mapped_column(String(50))


class DroneFlightLog(Base, TimestampMixin):
    __tablename__ = "drone_flight_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drone_id: Mapped[str] = mapped_column(String(20), nullable=False)  # SPRAY-1, SURVEY-1
    flight_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    takeoff_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    landing_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    flight_type: Mapped[str] = mapped_column(String(20), nullable=False)  # spraying, survey, ndvi, inspection
    area_covered_sqm: Mapped[float] = mapped_column(Float, default=0)
    altitude_m: Mapped[float] = mapped_column(Float, default=5)
    speed_ms: Mapped[float] = mapped_column(Float, default=3)
    chemical_used: Mapped[Optional[str]] = mapped_column(String(100))
    chemical_volume_liters: Mapped[Optional[float]] = mapped_column(Float)
    battery_start_pct: Mapped[float] = mapped_column(Float, default=100)
    battery_end_pct: Mapped[Optional[float]] = mapped_column(Float)
    images_captured: Mapped[int] = mapped_column(Integer, default=0)
    ndvi_data_path: Mapped[Optional[str]] = mapped_column(String(200))
    anomalies_detected: Mapped[int] = mapped_column(Integer, default=0)
    pilot: Mapped[Optional[str]] = mapped_column(String(50))
    weather_conditions: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="completed")
    notes: Mapped[Optional[str]] = mapped_column(Text)
