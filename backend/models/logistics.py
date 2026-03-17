"""Delivery routes, trips, per-order delivery tracking, and cold-chain shipments."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
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


# ═══════════════════════════════════════════════════════════════
# COLD-CHAIN MODULE
# ═══════════════════════════════════════════════════════════════

# Temperature thresholds (°C) by product category
COLD_CHAIN_THRESHOLDS = {
    "fish":             8.0,
    "seafood":          8.0,
    "vegetables":      12.0,
    "fruits":          12.0,
    "dairy":            4.0,
    "poultry_products": 4.0,
    "eggs":            10.0,
    "honey":           25.0,   # ambient is fine; flag only above 25
}


class Vehicle(Base, TimestampMixin):
    """Farm-owned delivery fleet."""
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(30), default="tempo")
    # bike | auto | tempo | truck | refrigerated_truck | van
    make: Mapped[Optional[str]] = mapped_column(String(50))
    model: Mapped[Optional[str]] = mapped_column(String(50))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    capacity_kg: Mapped[float] = mapped_column(Float, default=0)
    refrigerated: Mapped[bool] = mapped_column(Boolean, default=False)
    temp_min_c: Mapped[Optional[float]] = mapped_column(Float)   # design operating min
    temp_max_c: Mapped[Optional[float]] = mapped_column(Float)   # design operating max
    insurance_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_service_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    shipments: Mapped[List["ColdChainShipment"]] = relationship(
        "ColdChainShipment", back_populates="vehicle"
    )


class ColdChainShipment(Base, TimestampMixin):
    """Temperature-controlled shipment from farm to city buyer."""
    __tablename__ = "cold_chain_shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vehicles.id"))
    driver_employee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"))
    # Route
    origin_city: Mapped[str] = mapped_column(String(100), default="Rajapalayam Farm")
    destination_city: Mapped[str] = mapped_column(String(100))
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    # Product details
    product_category: Mapped[str] = mapped_column(String(30))
    # fish | seafood | vegetables | fruits | dairy | poultry_products | eggs | honey
    product_lots: Mapped[Optional[dict]] = mapped_column(JSON)
    # e.g. [{"lot_id": "LOT-001", "product": "Murrel", "quantity_kg": 120}]
    total_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    # Temperature requirements
    required_temp_min_c: Mapped[Optional[float]] = mapped_column(Float)
    required_temp_max_c: Mapped[Optional[float]] = mapped_column(Float)
    # Timeline
    dispatch_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    eta: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # Status: scheduled | dispatched | in_transit | delivered | partially_rejected | fully_rejected
    status: Mapped[str] = mapped_column(String(30), default="scheduled")
    has_temperature_breach: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="shipments")
    temperature_logs: Mapped[List["ShipmentTemperatureLog"]] = relationship(
        "ShipmentTemperatureLog", back_populates="shipment", cascade="all, delete-orphan"
    )
    delivery_confirmation: Mapped[Optional["ShipmentDeliveryConfirmation"]] = relationship(
        "ShipmentDeliveryConfirmation", back_populates="shipment", uselist=False,
        cascade="all, delete-orphan"
    )
    rejections: Mapped[List["ShipmentRejection"]] = relationship(
        "ShipmentRejection", back_populates="shipment", cascade="all, delete-orphan"
    )


class ShipmentTemperatureLog(Base):
    """Temperature readings logged every ~30 min during transit."""
    __tablename__ = "shipment_temperature_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("cold_chain_shipments.id"), index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float)
    location: Mapped[Optional[str]] = mapped_column(String(200))   # GPS coords or city name
    is_breach: Mapped[bool] = mapped_column(Boolean, default=False)
    breach_threshold_c: Mapped[Optional[float]] = mapped_column(Float)
    recorded_by: Mapped[Optional[str]] = mapped_column(String(100))

    shipment: Mapped["ColdChainShipment"] = relationship(
        "ColdChainShipment", back_populates="temperature_logs"
    )


class ShipmentDeliveryConfirmation(Base):
    """Proof-of-delivery record (one per shipment)."""
    __tablename__ = "shipment_delivery_confirmations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cold_chain_shipments.id"), unique=True
    )
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(150))
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(20))
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    delivered_weight_kg: Mapped[float] = mapped_column(Float, default=0)
    temperature_at_delivery_c: Mapped[Optional[float]] = mapped_column(Float)
    is_temperature_compliant: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    shipment: Mapped["ColdChainShipment"] = relationship(
        "ColdChainShipment", back_populates="delivery_confirmation"
    )


class ShipmentRejection(Base, TimestampMixin):
    """Customer rejection record with optional partial credit note."""
    __tablename__ = "shipment_rejections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("cold_chain_shipments.id"), index=True)
    rejected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rejection_reason: Mapped[str] = mapped_column(String(300))
    # temperature_breach | quality_issue | weight_short | damaged_packaging | wrong_product | other
    rejected_quantity_kg: Mapped[float] = mapped_column(Float, default=0)
    accepted_quantity_kg: Mapped[float] = mapped_column(Float, default=0)
    credit_note_number: Mapped[Optional[str]] = mapped_column(String(50))
    credit_note_amount: Mapped[float] = mapped_column(Float, default=0)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    customer_name: Mapped[Optional[str]] = mapped_column(String(150))
    raised_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    shipment: Mapped["ColdChainShipment"] = relationship(
        "ColdChainShipment", back_populates="rejections"
    )
