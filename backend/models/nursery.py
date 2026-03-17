"""Nursery management models — seedling batches and B2B orders."""
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, Boolean, Text, ForeignKey
from backend.models.base import Base, TimestampMixin, SoftDeleteMixin

class NurseryBatch(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "nursery_batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    species: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="vegetable")  # vegetable/flower/tree/herb/aquatic
    sowing_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_ready_date: Mapped[Optional[date]] = mapped_column(Date)
    tray_count: Mapped[int] = mapped_column(Integer, default=0)
    cells_per_tray: Mapped[int] = mapped_column(Integer, default=98)
    germination_pct: Mapped[float] = mapped_column(Float, default=0.0)
    seedlings_ready: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="sown")  # sown/germinated/hardening/ready/dispatched
    notes: Mapped[Optional[str]] = mapped_column(Text)

    orders: Mapped[List["NurseryOrder"]] = relationship("NurseryOrder", back_populates="batch")

class NurseryOrder(Base, TimestampMixin):
    __tablename__ = "nursery_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("nursery_batches.id"))
    buyer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    buyer_contact: Mapped[Optional[str]] = mapped_column(String(50))
    species: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    price_per_seedling: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    dispatch_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/confirmed/dispatched/delivered/cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text)

    batch: Mapped[Optional["NurseryBatch"]] = relationship("NurseryBatch", back_populates="orders")
