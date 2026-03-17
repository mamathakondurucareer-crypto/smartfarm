"""Drone fleet management models."""
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, Boolean, Text, ForeignKey
from backend.models.base import Base, TimestampMixin, SoftDeleteMixin

class Drone(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "drones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drone_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    drone_type: Mapped[str] = mapped_column(String(50), default="spray")  # spray/survey/multi
    battery_health_pct: Mapped[float] = mapped_column(Float, default=100.0)
    last_maintenance: Mapped[Optional[date]] = mapped_column(Date)
    total_flight_hours: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="ready")  # ready/in_flight/maintenance/retired
    notes: Mapped[Optional[str]] = mapped_column(Text)

    flights: Mapped[List["DroneFlightLog"]] = relationship("DroneFlightLog", back_populates="drone")

class DroneFlightLog(Base, TimestampMixin):
    __tablename__ = "drone_flight_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drone_id: Mapped[int] = mapped_column(Integer, ForeignKey("drones.id"), nullable=False)
    flight_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mission_type: Mapped[str] = mapped_column(String(30), nullable=False)  # spray/survey/ndvi/inspection
    area_covered_ha: Mapped[float] = mapped_column(Float, default=0.0)
    duration_mins: Mapped[int] = mapped_column(Integer, default=0)
    pilot: Mapped[str] = mapped_column(String(100), nullable=False)
    zone: Mapped[Optional[str]] = mapped_column(String(100))
    ndvi_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-1 for survey missions
    notes: Mapped[Optional[str]] = mapped_column(Text)

    drone: Mapped["Drone"] = relationship("Drone", back_populates="flights")
    spraying: Mapped[Optional["DroneSprayLog"]] = relationship("DroneSprayLog", back_populates="flight", uselist=False)

class DroneSprayLog(Base, TimestampMixin):
    __tablename__ = "drone_spray_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_id: Mapped[int] = mapped_column(Integer, ForeignKey("drone_flight_logs.id"), nullable=False, unique=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)  # chemical/bio-agent applied
    agent_type: Mapped[str] = mapped_column(String(30), default="bio")  # bio/chemical/fertiliser
    dosage_per_ha: Mapped[float] = mapped_column(Float, default=0.0)
    total_volume_l: Mapped[float] = mapped_column(Float, default=0.0)
    gps_zone_coords: Mapped[Optional[str]] = mapped_column(Text)  # JSON polygon
    notes: Mapped[Optional[str]] = mapped_column(Text)

    flight: Mapped["DroneFlightLog"] = relationship("DroneFlightLog", back_populates="spraying")
