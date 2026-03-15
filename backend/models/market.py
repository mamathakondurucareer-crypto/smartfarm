"""Market prices, customers, orders, and shipment tracking."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin, SoftDeleteMixin


class MarketPrice(Base, TimestampMixin):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    market_city: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)  # fish, vegetable, egg, spice
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    avg_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), default="kg")
    volume_traded: Mapped[Optional[float]] = mapped_column(Float)
    trend: Mapped[str] = mapped_column(String(10), default="stable")  # up, down, stable
    source: Mapped[str] = mapped_column(String(30), default="manual")  # manual, api, agmarknet


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: wholesale, retail, restaurant, hotel, supermarket, online_platform, institutional, export
    contact_person: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    gstin: Mapped[Optional[str]] = mapped_column(String(15))
    credit_limit: Mapped[float] = mapped_column(Float, default=0)
    outstanding_balance: Mapped[float] = mapped_column(Float, default=0)
    payment_terms: Mapped[str] = mapped_column(String(30), default="cod")
    rating: Mapped[float] = mapped_column(Float, default=3.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    orders: Mapped[List["CustomerOrder"]] = relationship("CustomerOrder", back_populates="customer")


class CustomerOrder(Base, TimestampMixin):
    __tablename__ = "customer_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date)
    delivery_city: Mapped[str] = mapped_column(String(50), nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    gst_amount: Mapped[float] = mapped_column(Float, default=0)
    transport_charges: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")
    order_status: Mapped[str] = mapped_column(String(20), default="confirmed")
    # Status: confirmed, processing, packed, shipped, delivered, cancelled, returned
    notes: Mapped[Optional[str]] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_orders.id"), nullable=False)
    product: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    gst_rate: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["CustomerOrder"] = relationship("CustomerOrder", back_populates="items")


class Shipment(Base, TimestampMixin):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shipment_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_orders.id"), nullable=False)
    dispatch_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expected_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    vehicle_number: Mapped[Optional[str]] = mapped_column(String(15))
    driver_name: Mapped[Optional[str]] = mapped_column(String(50))
    driver_phone: Mapped[Optional[str]] = mapped_column(String(15))
    transport_mode: Mapped[str] = mapped_column(String(20), default="truck")
    # Modes: truck, refrigerated_truck, tempo, own_vehicle, courier
    origin: Mapped[str] = mapped_column(String(50), default="Nellore Farm")
    destination_city: Mapped[str] = mapped_column(String(50), nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, default=0)
    transport_cost: Mapped[float] = mapped_column(Float, default=0)
    cold_chain: Mapped[bool] = mapped_column(Boolean, default=False)
    temperature_maintained: Mapped[Optional[str]] = mapped_column(String(20))
    total_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="dispatched")
    # Status: dispatched, in_transit, delivered, returned
    delivery_proof: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["CustomerOrder"] = relationship("CustomerOrder", back_populates="shipments")
    items: Mapped[List["ShipmentItem"]] = relationship("ShipmentItem", back_populates="shipment")


class ShipmentItem(Base):
    __tablename__ = "shipment_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("shipments.id"), nullable=False)
    product: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    packaging: Mapped[str] = mapped_column(String(30), default="crate")
    temperature_requirement: Mapped[Optional[str]] = mapped_column(String(20))

    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="items")
