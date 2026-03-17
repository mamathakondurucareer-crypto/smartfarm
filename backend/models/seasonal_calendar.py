"""Seasonal Operations Scheduler — monthly tasks, crop rotation plans."""

from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class SeasonalTask(Base, TimestampMixin):
    """A recurring seasonal task tied to a specific month (1–12)."""
    __tablename__ = "seasonal_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)   # 1–12
    week: Mapped[Optional[int]] = mapped_column(Integer)                       # 1–4 within month
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # Categories: aquaculture | crops | poultry | harvest | nursery | soil_prep |
    #             irrigation | marketing | maintenance | training | compliance
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class SeasonalTaskCompletion(Base, TimestampMixin):
    """Log of completed seasonal tasks for a specific year."""
    __tablename__ = "seasonal_task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("seasonal_tasks.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    outcome: Mapped[Optional[str]] = mapped_column(Text)
    completed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class CropRotationPlan(Base, TimestampMixin):
    """Crop rotation plan for a field / zone across months."""
    __tablename__ = "crop_rotation_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_or_zone: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[Optional[str]] = mapped_column(String(100))
    sowing_month: Mapped[int] = mapped_column(Integer, nullable=False)   # 1–12
    harvest_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–12
    area_sq_meters: Mapped[Optional[float]] = mapped_column()
    expected_yield_kg: Mapped[Optional[float]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(Text)
