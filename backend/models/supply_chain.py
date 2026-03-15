"""Farm-to-store supply chain: transfers and store stock."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.base import TimestampMixin


class FarmSupplyTransfer(Base, TimestampMixin):
    __tablename__ = "farm_supply_transfers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transfer_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    transfer_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source_type: Mapped[str] = mapped_column(String(30))  # pond|greenhouse|vertical_farm|poultry|packhouse
    source_id: Mapped[Optional[int]] = mapped_column(Integer)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_catalog.id"))
    product_name: Mapped[str] = mapped_column(String(100))
    quantity_transferred: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    quality_grade: Mapped[str] = mapped_column(String(5), default="A")
    cost_per_unit: Mapped[float] = mapped_column(Float, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0)
    transferred_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    received_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|in_transit|received|rejected
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    product: Mapped["ProductCatalog"] = relationship("ProductCatalog")  # type: ignore[name-defined]


class StoreStock(Base):
    __tablename__ = "store_stock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_catalog.id"), unique=True)
    current_qty: Mapped[float] = mapped_column(Float, default=0)
    reserved_qty: Mapped[float] = mapped_column(Float, default=0)
    unit: Mapped[str] = mapped_column(String(20))
    avg_cost_per_unit: Mapped[float] = mapped_column(Float, default=0)
    last_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String(30), default="floor")  # floor|cold_room|backstore
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    product: Mapped["ProductCatalog"] = relationship("ProductCatalog", back_populates="store_stock")  # type: ignore[name-defined]

    @property
    def available_qty(self) -> float:
        return max(0.0, self.current_qty - self.reserved_qty)

    @property
    def total_value(self) -> float:
        return round(self.current_qty * self.avg_cost_per_unit, 2)
