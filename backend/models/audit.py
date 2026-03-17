"""Audit log and reporting calendar — scheduled reports, audit trail, export history."""

from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class AuditLog(Base):
    """Immutable record of every create/update/delete action across the system."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    username: Mapped[Optional[str]] = mapped_column(String(50))   # denormalised for tombstone safety
    action: Mapped[str] = mapped_column(String(30), nullable=False)  # CREATE | UPDATE | DELETE | LOGIN | EXPORT
    resource: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Employee", "PayrollRun"
    resource_id: Mapped[Optional[str]] = mapped_column(String(50))
    detail: Mapped[Optional[str]] = mapped_column(Text)             # JSON diff or description
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))


class ReportSchedule(Base, TimestampMixin):
    """Scheduled report definition — what to generate, when, and who to notify."""
    __tablename__ = "report_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    report_type: Mapped[str] = mapped_column(String(80), nullable=False)
    # payroll_monthly | attendance_weekly | harvest_weekly | inventory_weekly
    # financial_monthly | disease_weekly | energy_monthly | water_monthly | compliance_monthly
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)  # daily | weekly | monthly | quarterly
    next_run_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    recipients: Mapped[Optional[str]] = mapped_column(Text)  # comma-separated emails
    output_format: Mapped[str] = mapped_column(String(10), default="pdf")  # pdf | csv | xlsx
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ReportExecution(Base, TimestampMixin):
    """Each time a scheduled (or manual) report was generated."""
    __tablename__ = "report_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("report_schedules.id"))
    report_type: Mapped[str] = mapped_column(String(80), nullable=False)
    triggered_by: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled | manual
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running")  # running | success | failed
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    requested_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    parameters: Mapped[Optional[str]] = mapped_column(Text)  # JSON filter params
