"""Inventory management: categories, items, transactions, purchase orders, suppliers."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin, SoftDeleteMixin


class InventoryCategory(Base, TimestampMixin):
    __tablename__ = "inventory_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("inventory_categories.id"))
    # Categories: fish_feed, poultry_feed, seeds, fertilizers, chemicals, packaging,
    #             equipment_parts, fuel, office_supplies, safety_gear, etc.

    items: Mapped[List["InventoryItem"]] = relationship("InventoryItem", back_populates="category")


class Supplier(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    supplier_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: feed, seed, chemical, equipment, packaging, solar, greenhouse, iot, drone, general
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    gstin: Mapped[Optional[str]] = mapped_column(String(15))
    pan: Mapped[Optional[str]] = mapped_column(String(10))
    bank_account: Mapped[Optional[str]] = mapped_column(String(20))
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(11))
    payment_terms: Mapped[str] = mapped_column(String(30), default="net_30")
    rating: Mapped[float] = mapped_column(Float, default=3.0)  # 1-5
    notes: Mapped[Optional[str]] = mapped_column(Text)

    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier")


class InventoryItem(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventory_categories.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # kg, litres, units, bags, rolls
    current_stock: Mapped[float] = mapped_column(Float, default=0)
    minimum_stock: Mapped[float] = mapped_column(Float, default=0)
    maximum_stock: Mapped[float] = mapped_column(Float, default=0)
    reorder_point: Mapped[float] = mapped_column(Float, default=0)
    reorder_quantity: Mapped[float] = mapped_column(Float, default=0)
    unit_cost: Mapped[float] = mapped_column(Float, default=0)
    total_value: Mapped[float] = mapped_column(Float, default=0)
    location: Mapped[str] = mapped_column(String(50), default="main_store")
    shelf_life_days: Mapped[Optional[int]] = mapped_column(Integer)
    preferred_supplier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("suppliers.id"))
    hsn_code: Mapped[Optional[str]] = mapped_column(String(10))
    gst_rate: Mapped[float] = mapped_column(Float, default=0)

    category: Mapped["InventoryCategory"] = relationship("InventoryCategory", back_populates="items")
    transactions: Mapped[List["InventoryTransaction"]] = relationship("InventoryTransaction", back_populates="item")

    @property
    def is_low_stock(self) -> bool:
        return self.current_stock <= self.reorder_point

    @property
    def stock_status(self) -> str:
        if self.current_stock <= 0:
            return "out_of_stock"
        if self.current_stock <= self.reorder_point:
            return "low"
        if self.current_stock >= self.maximum_stock:
            return "overstocked"
        return "adequate"


class InventoryTransaction(Base, TimestampMixin):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Types: purchase, consumption, return, adjustment, transfer, wastage, production_in
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(30))  # po, feed_log, crop_activity, etc.
    reference_id: Mapped[Optional[int]] = mapped_column(Integer)
    department: Mapped[Optional[str]] = mapped_column(String(30))
    performed_by: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="transactions")


class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    po_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expected_delivery: Mapped[Optional[date]] = mapped_column(Date)
    actual_delivery: Mapped[Optional[date]] = mapped_column(Date)
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    gst_amount: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")
    # Status: pending, partial, paid, overdue
    delivery_status: Mapped[str] = mapped_column(String(20), default="ordered")
    # Status: ordered, shipped, delivered, partial_delivery, cancelled
    approved_by: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="purchase_orders")
    items: Mapped[List["PurchaseOrderItem"]] = relationship("PurchaseOrderItem", back_populates="purchase_order")


class PurchaseOrderItem(Base, TimestampMixin):
    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_ordered: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_received: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    gst_rate: Mapped[float] = mapped_column(Float, default=0)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", back_populates="items")
