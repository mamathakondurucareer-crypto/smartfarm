"""Automation rules engine and execution logs."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey
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
