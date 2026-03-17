"""Agri-Tourism / Farm Visit module — packages, bookings, visitor groups, revenue."""

from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class VisitPackage(Base, TimestampMixin):
    """Farm tour / agri-tourism package definitions."""
    __tablename__ = "visit_packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    package_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: farm_tour | school_visit | corporate_outing | agri_camp | weekend_stay
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    max_group_size: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    price_per_person: Mapped[float] = mapped_column(Float, nullable=False)
    min_age_years: Mapped[Optional[int]] = mapped_column(Integer)
    includes_meal: Mapped[bool] = mapped_column(Boolean, default=False)
    includes_activity: Mapped[Optional[str]] = mapped_column(Text)  # comma-separated activities
    available_days: Mapped[Optional[str]] = mapped_column(String(100))  # e.g. "Mon,Wed,Fri,Sat,Sun"
    slots_per_day: Mapped[int] = mapped_column(Integer, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class VisitorGroup(Base, TimestampMixin):
    """Visitor group / organisation details."""
    __tablename__ = "visitor_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_name: Mapped[str] = mapped_column(String(150), nullable=False)
    group_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: school | college | corporate | family | ngo | government | individual
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(120))
    city: Mapped[Optional[str]] = mapped_column(String(80))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class VisitBooking(Base, TimestampMixin):
    """Individual farm visit booking."""
    __tablename__ = "visit_bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(Integer, ForeignKey("visit_packages.id"), nullable=False)
    visitor_group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("visitor_groups.id"))
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    time_slot: Mapped[Optional[str]] = mapped_column(String(20))  # "09:00" | "14:00"
    pax_count: Mapped[int] = mapped_column(Integer, nullable=False)
    guide_assigned: Mapped[Optional[str]] = mapped_column(String(100))
    price_per_person: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    advance_paid: Mapped[float] = mapped_column(Float, default=0.0)
    balance_due: Mapped[float] = mapped_column(Float, default=0.0)
    payment_mode: Mapped[Optional[str]] = mapped_column(String(30))  # cash | upi | bank_transfer
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # Status: pending | confirmed | completed | cancelled | no_show
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1–5
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text)
    confirmed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class TourRevenueEntry(Base, TimestampMixin):
    """Revenue log entry for completed farm visits."""
    __tablename__ = "tour_revenue_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("visit_bookings.id"), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount_received: Mapped[float] = mapped_column(Float, nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    received_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
