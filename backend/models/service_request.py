"""Maintenance and repair service requests."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.base import TimestampMixin


class ServiceRequest(Base, TimestampMixin):
    __tablename__ = "service_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    requested_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"))
    department: Mapped[str] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low|medium|high|urgent
    category: Mapped[str] = mapped_column(String(30))  # maintenance|repair|installation|cleaning|inspection
    affected_equipment: Mapped[Optional[str]] = mapped_column(String(200))
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)
    actual_cost: Mapped[float] = mapped_column(Float, default=0)
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="open")  # open|assigned|in_progress|pending_parts|resolved|closed
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
