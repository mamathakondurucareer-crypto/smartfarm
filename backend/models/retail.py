"""POS sessions, transactions, and retail customer loyalty."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.base import TimestampMixin


class POSSession(Base, TimestampMixin):
    __tablename__ = "pos_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    cashier_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opening_cash: Mapped[float] = mapped_column(Float, default=0)
    closing_cash: Mapped[Optional[float]] = mapped_column(Float)
    total_sales: Mapped[float] = mapped_column(Float, default=0)
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open|closed|suspended
    notes: Mapped[Optional[str]] = mapped_column(Text)
    transactions: Mapped[List["POSTransaction"]] = relationship("POSTransaction", back_populates="session")


class POSTransaction(Base, TimestampMixin):
    __tablename__ = "pos_transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("pos_sessions.id"))
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id"))
    cashier_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    transaction_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    amount_tendered: Mapped[float] = mapped_column(Float, default=0)
    change_given: Mapped[float] = mapped_column(Float, default=0)
    payment_mode: Mapped[str] = mapped_column(String(20), default="cash")  # cash|upi|card|credit
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="completed")  # completed|voided|refunded
    invoice_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("invoices.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    session: Mapped["POSSession"] = relationship("POSSession", back_populates="transactions")
    items: Mapped[List["POSTransactionItem"]] = relationship(
        "POSTransactionItem", back_populates="transaction", cascade="all, delete-orphan"
    )


class POSTransactionItem(Base):
    __tablename__ = "pos_transaction_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(Integer, ForeignKey("pos_transactions.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_catalog.id"))
    product_name: Mapped[str] = mapped_column(String(100))
    barcode: Mapped[Optional[str]] = mapped_column(String(50))
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    unit_price: Mapped[float] = mapped_column(Float)
    discount_pct: Mapped[float] = mapped_column(Float, default=0)
    tax_rate: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float)
    transaction: Mapped["POSTransaction"] = relationship("POSTransaction", back_populates="items")
    product: Mapped["ProductCatalog"] = relationship("ProductCatalog")  # type: ignore[name-defined]
