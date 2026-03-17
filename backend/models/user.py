"""User authentication, roles, employee HR, attendance, and leave management."""

from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, Date, DateTime, Text,
    ForeignKey, Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from backend.database import Base
from backend.models.base import TimestampMixin, SoftDeleteMixin


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    WORKER = "worker"
    VIEWER = "viewer"
    STORE_MANAGER = "store_manager"
    CASHIER       = "cashier"
    PACKER        = "packer"
    DRIVER        = "driver"
    SCANNER       = "scanner"


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    permissions: Mapped[Optional[str]] = mapped_column(Text)  # JSON string of permissions

    users: Mapped[List["User"]] = relationship("User", back_populates="role")


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    employee: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="user", uselist=False)


class DepartmentEnum(str, enum.Enum):
    AQUACULTURE = "aquaculture"
    GREENHOUSE = "greenhouse"
    POULTRY = "poultry"
    FIELD_CROPS = "field_crops"
    NURSERY = "nursery"
    PACKHOUSE = "packhouse"
    MAINTENANCE = "maintenance"
    MANAGEMENT = "management"
    TECHNOLOGY = "technology"
    STORE      = "store"
    LOGISTICS  = "logistics"


class Employee(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    designation: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(15))
    address: Mapped[Optional[str]] = mapped_column(Text)
    aadhar_number: Mapped[Optional[str]] = mapped_column(String(12))
    pan_number: Mapped[Optional[str]] = mapped_column(String(10))
    bank_account: Mapped[Optional[str]] = mapped_column(String(20))
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(11))
    base_salary: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    hra: Mapped[float] = mapped_column(Float, default=0)
    pf_number: Mapped[Optional[str]] = mapped_column(String(22))
    esi_number: Mapped[Optional[str]] = mapped_column(String(17))
    employment_type: Mapped[str] = mapped_column(String(20), default="permanent")  # permanent, contract, seasonal
    shift: Mapped[Optional[str]] = mapped_column(String(20))  # morning, evening, night

    user: Mapped[Optional["User"]] = relationship("User", back_populates="employee")
    attendance_records: Mapped[List["Attendance"]] = relationship("Attendance", back_populates="employee")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship("LeaveRequest", back_populates="employee")


class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # present, absent, half_day, leave, holiday
    overtime_hours: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="attendance_records")


class LeaveRequest(Base, TimestampMixin):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type: Mapped[str] = mapped_column(String(20), nullable=False)  # casual, sick, earned, unpaid
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))

    employee: Mapped["Employee"] = relationship("Employee", back_populates="leave_requests")


class LeaveBalance(Base, TimestampMixin):
    """Annual leave entitlement and balance per employee per leave type."""
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    leave_type: Mapped[str] = mapped_column(String(20), nullable=False)  # casual | sick | earned | unpaid
    entitled_days: Mapped[int] = mapped_column(Integer, default=0)
    taken_days: Mapped[float] = mapped_column(Float, default=0)
    # remaining = entitled - taken (computed in application layer)

    employee: Mapped["Employee"] = relationship("Employee")


class PayrollRun(Base, TimestampMixin):
    """Monthly payroll calculation per employee."""
    __tablename__ = "payroll_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)   # 1–12
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # Earnings
    basic_salary: Mapped[float] = mapped_column(Float, default=0)
    hra: Mapped[float] = mapped_column(Float, default=0)
    other_allowances: Mapped[float] = mapped_column(Float, default=0)
    overtime_hours: Mapped[float] = mapped_column(Float, default=0)
    ot_pay: Mapped[float] = mapped_column(Float, default=0)       # 2× hourly for >48 hrs/week
    gross_salary: Mapped[float] = mapped_column(Float, default=0)
    # Deductions
    pf_employee: Mapped[float] = mapped_column(Float, default=0)  # 12% of basic
    pf_employer: Mapped[float] = mapped_column(Float, default=0)  # 12% of basic
    esi_employee: Mapped[float] = mapped_column(Float, default=0) # 0.75% of gross
    esi_employer: Mapped[float] = mapped_column(Float, default=0) # 3.25% of gross
    tds: Mapped[float] = mapped_column(Float, default=0)
    other_deductions: Mapped[float] = mapped_column(Float, default=0)
    total_deductions: Mapped[float] = mapped_column(Float, default=0)
    net_pay: Mapped[float] = mapped_column(Float, default=0)
    # Attendance summary for the month
    working_days: Mapped[int] = mapped_column(Integer, default=26)
    present_days: Mapped[float] = mapped_column(Float, default=0)
    absent_days: Mapped[float] = mapped_column(Float, default=0)
    leave_days: Mapped[float] = mapped_column(Float, default=0)
    # Meta
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | processed | paid
    payslip_url: Mapped[Optional[str]] = mapped_column(String(500))
    processed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship("Employee")


class PerformanceReview(Base, TimestampMixin):
    """Quarterly/annual performance review per employee."""
    __tablename__ = "performance_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    review_period: Mapped[str] = mapped_column(String(20), nullable=False)  # Q1_2025, Q2_2025, Annual_2025
    review_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Scores (1–5)
    productivity_score: Mapped[float] = mapped_column(Float, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0)
    punctuality_score: Mapped[float] = mapped_column(Float, default=0)
    teamwork_score: Mapped[float] = mapped_column(Float, default=0)
    overall_score: Mapped[float] = mapped_column(Float, default=0)  # computed avg
    # Narrative
    strengths: Mapped[Optional[str]] = mapped_column(Text)
    areas_for_improvement: Mapped[Optional[str]] = mapped_column(Text)
    recommended_increment_pct: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | final
    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship("Employee")


class TrainingRecord(Base, TimestampMixin):
    """Employee training and certification log."""
    __tablename__ = "training_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    training_name: Mapped[str] = mapped_column(String(200), nullable=False)
    training_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # safety | technical | compliance | soft_skills | on_the_job | external
    conducted_by: Mapped[Optional[str]] = mapped_column(String(150))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[float] = mapped_column(Float, default=0)
    score: Mapped[Optional[float]] = mapped_column(Float)        # 0–100 if assessed
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled | completed | failed
    notes: Mapped[Optional[str]] = mapped_column(Text)

    employee: Mapped["Employee"] = relationship("Employee")
