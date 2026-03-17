"""Government Subsidy Tracker — schemes, applications, disbursements."""

from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class SubsidyScheme(Base, TimestampMixin):
    """Government subsidy scheme definition (PMKSY, RKVY, NABARD, etc.)."""
    __tablename__ = "subsidy_schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    ministry: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    # Categories: irrigation | greenhouse | cold_chain | fisheries | poultry | solar | general
    subsidy_pct: Mapped[Optional[float]] = mapped_column(Float)   # e.g. 55.0 for 55%
    max_amount: Mapped[Optional[float]] = mapped_column(Float)    # absolute cap in INR
    description: Mapped[Optional[str]] = mapped_column(Text)
    eligibility: Mapped[Optional[str]] = mapped_column(Text)
    apply_url: Mapped[Optional[str]] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_till: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class SubsidyApplication(Base, TimestampMixin):
    """Application lodged for a government subsidy scheme."""
    __tablename__ = "subsidy_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scheme_id: Mapped[int] = mapped_column(Integer, ForeignKey("subsidy_schemes.id"), nullable=False)
    application_number: Mapped[Optional[str]] = mapped_column(String(80))
    applied_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    project_description: Mapped[Optional[str]] = mapped_column(Text)
    project_cost: Mapped[float] = mapped_column(Float, nullable=False)
    claimed_subsidy_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="submitted")
    # Status: submitted | under_review | approved | rejected | disbursed | lapsed
    approved_amount: Mapped[Optional[float]] = mapped_column(Float)
    approval_date: Mapped[Optional[date]] = mapped_column(Date)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    documents_submitted: Mapped[Optional[str]] = mapped_column(Text)  # comma-sep doc names
    submitted_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class DisbursementRecord(Base, TimestampMixin):
    """Actual disbursement received for an approved subsidy application."""
    __tablename__ = "disbursement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("subsidy_applications.id"), nullable=False)
    disbursement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount_received: Mapped[float] = mapped_column(Float, nullable=False)
    payment_mode: Mapped[Optional[str]] = mapped_column(String(30))  # bank_transfer | cheque | PFMS
    reference_number: Mapped[Optional[str]] = mapped_column(String(80))
    bank_account: Mapped[Optional[str]] = mapped_column(String(30))
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
