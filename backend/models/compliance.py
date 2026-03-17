"""Compliance & Licence Tracker models."""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, Boolean, Text, ForeignKey, DateTime
from backend.models.base import Base, TimestampMixin

class Licence(Base, TimestampMixin):
    __tablename__ = "licences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100))  # environmental/food_safety/labour/financial/aquaculture/organic
    issuing_authority: Mapped[str] = mapped_column(String(200), nullable=False)
    licence_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    cost_inr: Mapped[float] = mapped_column(Float, default=0.0)
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    renewal_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/expiring/expired/pending
    document_url: Mapped[Optional[str]] = mapped_column(String(500))
    responsible_person: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

class ComplianceTask(Base, TimestampMixin):
    __tablename__ = "compliance_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    task_type: Mapped[str] = mapped_column(String(50))  # monthly_gst/quarterly_audit/annual_itr/safety_drill/etc.
    frequency: Mapped[str] = mapped_column(String(30), default="monthly")  # daily/weekly/monthly/quarterly/annual
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)
    document_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
