"""Packing orders, items, and barcode registry."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.base import TimestampMixin


class PackingOrder(Base, TimestampMixin):
    __tablename__ = "packing_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    packing_order_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    order_ref_type: Mapped[str] = mapped_column(String(30))  # customer_order|store_stock|transfer
    order_ref_id: Mapped[Optional[int]] = mapped_column(Integer)
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"))
    scheduled_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|in_progress|completed|paused
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    items: Mapped[List["PackingOrderItem"]] = relationship(
        "PackingOrderItem", back_populates="packing_order", cascade="all, delete-orphan"
    )


class PackingOrderItem(Base):
    __tablename__ = "packing_order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    packing_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("packing_orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_catalog.id"))
    product_name: Mapped[str] = mapped_column(String(100))
    quantity_required: Mapped[float] = mapped_column(Float)
    quantity_packed: Mapped[float] = mapped_column(Float, default=0)
    packaging_type: Mapped[Optional[str]] = mapped_column(String(50))
    label_printed: Mapped[bool] = mapped_column(Boolean, default=False)
    barcode_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    packing_order: Mapped["PackingOrder"] = relationship("PackingOrder", back_populates="items")
    product: Mapped["ProductCatalog"] = relationship("ProductCatalog")  # type: ignore[name-defined]


class BarcodeRegistry(Base, TimestampMixin):
    __tablename__ = "barcode_registry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    barcode: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(30))  # product|batch|packing_order|asset
    entity_id: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_catalog.id"))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    generated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scanned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scan_count: Mapped[int] = mapped_column(Integer, default=0)
