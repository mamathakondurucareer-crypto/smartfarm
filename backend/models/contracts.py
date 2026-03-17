"""Contract Farming & Consulting module — contracts, service logs, invoices, neighbouring farms."""

from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class NeighbouringFarm(Base, TimestampMixin):
    """Neighbouring farm / client profile for contract farming and consulting."""
    __tablename__ = "neighbouring_farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_name: Mapped[str] = mapped_column(String(150), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(120))
    village: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(80))
    land_acres: Mapped[Optional[float]] = mapped_column(Float)
    current_crops: Mapped[Optional[str]] = mapped_column(Text)  # comma-separated
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ConsultingContract(Base, TimestampMixin):
    """Contract farming or consulting agreement."""
    __tablename__ = "consulting_contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    neighbouring_farm_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("neighbouring_farms.id"))
    client_name: Mapped[str] = mapped_column(String(150), nullable=False)  # denormalised
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: contract_farming | agri_consulting | input_supply | training | soil_testing | other
    scope: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    contract_value: Mapped[float] = mapped_column(Float, nullable=False)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(100))
    # e.g. "50% advance, 50% on completion"
    status: Mapped[str] = mapped_column(String(20), default="active")
    # Status: draft | active | completed | terminated
    total_billed: Mapped[float] = mapped_column(Float, default=0.0)
    total_received: Mapped[float] = mapped_column(Float, default=0.0)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ServiceDeliveryLog(Base, TimestampMixin):
    """Log of services delivered against a consulting contract."""
    __tablename__ = "service_delivery_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey("consulting_contracts.id"), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    hours_spent: Mapped[Optional[float]] = mapped_column(Float)
    materials_cost: Mapped[float] = mapped_column(Float, default=0.0)
    service_charge: Mapped[float] = mapped_column(Float, default=0.0)
    outcome: Mapped[Optional[str]] = mapped_column(Text)
    delivered_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ConsultingInvoice(Base, TimestampMixin):
    """Invoice raised against a consulting contract."""
    __tablename__ = "consulting_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey("consulting_contracts.id"), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="unpaid")
    # Status: unpaid | partial | paid | overdue | cancelled
    amount_received: Mapped[float] = mapped_column(Float, default=0.0)
    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    payment_mode: Mapped[Optional[str]] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
