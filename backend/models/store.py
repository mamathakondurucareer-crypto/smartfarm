"""Store configuration, product catalog, and pricing rules."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.base import TimestampMixin


class StoreConfig(Base, TimestampMixin):
    __tablename__ = "store_config"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_name: Mapped[str] = mapped_column(String(100), default="SmartFarm Store")
    store_code: Mapped[str] = mapped_column(String(20), unique=True)
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    gstin: Mapped[Optional[str]] = mapped_column(String(15))
    currency: Mapped[str] = mapped_column(String(5), default="INR")
    tax_inclusive: Mapped[bool] = mapped_column(Boolean, default=False)
    receipt_header: Mapped[Optional[str]] = mapped_column(Text)
    receipt_footer: Mapped[Optional[str]] = mapped_column(Text)
    default_payment_mode: Mapped[str] = mapped_column(String(20), default="cash")
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)


class ProductCatalog(Base, TimestampMixin):
    __tablename__ = "product_catalog"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50))  # fish, vegetables, eggs, honey, etc.
    source_type: Mapped[str] = mapped_column(String(20), default="farm_produced")  # farm_produced | purchased | both
    unit: Mapped[str] = mapped_column(String(20))  # kg, piece, dozen, litre
    selling_price: Mapped[float] = mapped_column(Float, default=0)
    mrp: Mapped[float] = mapped_column(Float, default=0)
    cost_price: Mapped[float] = mapped_column(Float, default=0)
    gst_rate: Mapped[float] = mapped_column(Float, default=0)
    hsn_code: Mapped[Optional[str]] = mapped_column(String(10))
    barcode: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    is_weighable: Mapped[bool] = mapped_column(Boolean, default=False)
    track_expiry: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # relationships
    store_stock: Mapped[Optional["StoreStock"]] = relationship("StoreStock", back_populates="product", uselist=False)
    price_rules: Mapped[List["PriceRule"]] = relationship("PriceRule", back_populates="product")


class PriceRule(Base, TimestampMixin):
    __tablename__ = "price_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_catalog.id"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(30))  # discount | tiered | seasonal | customer_specific
    customer_type: Mapped[Optional[str]] = mapped_column(String(30))
    min_quantity: Mapped[float] = mapped_column(Float, default=0)
    discount_pct: Mapped[float] = mapped_column(Float, default=0)
    fixed_price: Mapped[Optional[float]] = mapped_column(Float)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    product: Mapped["ProductCatalog"] = relationship("ProductCatalog", back_populates="price_rules")


# Avoid circular import — StoreStock is in supply_chain.py but referenced here
# The relationship is declared there; we import it lazily via string forward ref
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.models.supply_chain import StoreStock  # noqa: F401
