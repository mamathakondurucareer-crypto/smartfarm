"""Delivery routes, trips, and per-order delivery tracking."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from backend.models.base import TimestampMixin


class DeliveryRoute(Base, TimestampMixin):
    __tablename__ = "delivery_routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    route_code: Mapped[str] = mapped_column(String(20), unique=True)
    route_name: Mapped[str] = mapped_column(String(100))
    origin: Mapped[str] = mapped_column(String(200))
    destination: Mapped[str] = mapped_column(String(200))
    waypoints: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    distance_km: Mapped[float] = mapped_column(Float, default=0)
    estimated_duration_min: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class DeliveryTrip(Base, TimestampMixin):
    __tablename__ = "delivery_trips"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trip_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    route_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("delivery_routes.id"))
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    vehicle_number: Mapped[str] = mapped_column(String(20))
    vehicle_type: Mapped[str] = mapped_column(String(30), default="tempo")  # bike|auto|tempo|truck|refrigerated_truck
    planned_departure: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_departure: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_distance_km: Mapped[float] = mapped_column(Float, default=0)
    fuel_used_litres: Mapped[float] = mapped_column(Float, default=0)
    fuel_cost: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled|loading|in_transit|delivered|returned
    notes: Mapped[Optional[str]] = mapped_column(Text)
    route: Mapped[Optional["DeliveryRoute"]] = relationship("DeliveryRoute")
    trip_orders: Mapped[List["DeliveryTripOrder"]] = relationship(
        "DeliveryTripOrder", back_populates="trip", cascade="all, delete-orphan"
    )


class DeliveryTripOrder(Base):
    __tablename__ = "delivery_trip_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("delivery_trips.id"))
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_orders.id"))
    sequence_no: Mapped[int] = mapped_column(Integer, default=1)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|delivered|failed
    delivery_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    recipient_name: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    trip: Mapped["DeliveryTrip"] = relationship("DeliveryTrip", back_populates="trip_orders")
