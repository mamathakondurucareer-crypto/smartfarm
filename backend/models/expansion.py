"""Expansion Planning module — phases, milestones, CapEx tracking."""

from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class ExpansionPhase(Base, TimestampMixin):
    """A high-level expansion phase (e.g. Year 3 land acquisition, Year 4 GH3)."""
    __tablename__ = "expansion_phases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    planned_start: Mapped[Optional[date]] = mapped_column(Date)
    planned_end: Mapped[Optional[date]] = mapped_column(Date)
    actual_start: Mapped[Optional[date]] = mapped_column(Date)
    actual_end: Mapped[Optional[date]] = mapped_column(Date)
    total_budget: Mapped[float] = mapped_column(Float, default=0.0)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    # Status: planned | in_progress | completed | on_hold | cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ExpansionMilestone(Base, TimestampMixin):
    """A discrete milestone within an expansion phase."""
    __tablename__ = "expansion_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase_id: Mapped[int] = mapped_column(Integer, ForeignKey("expansion_phases.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_notes: Mapped[Optional[str]] = mapped_column(Text)
    owner: Mapped[Optional[str]] = mapped_column(String(100))  # person responsible
    priority: Mapped[str] = mapped_column(String(10), default="medium")  # high | medium | low
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    completed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))


class ExpansionCapex(Base, TimestampMixin):
    """Capital expenditure item for an expansion phase."""
    __tablename__ = "expansion_capex"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase_id: Mapped[int] = mapped_column(Integer, ForeignKey("expansion_phases.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    # Categories: land | civil_works | equipment | irrigation | solar | ict | livestock | other
    budgeted_amount: Mapped[float] = mapped_column(Float, nullable=False)
    actual_amount: Mapped[float] = mapped_column(Float, default=0.0)
    vendor: Mapped[Optional[str]] = mapped_column(String(150))
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    invoice_ref: Mapped[Optional[str]] = mapped_column(String(80))
    subsidy_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    subsidy_amount: Mapped[float] = mapped_column(Float, default=0.0)
    net_cost: Mapped[float] = mapped_column(Float, default=0.0)  # actual - subsidy
    notes: Mapped[Optional[str]] = mapped_column(Text)
