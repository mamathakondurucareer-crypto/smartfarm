"""Water system management — sources, tanks, irrigation zones, quality tests, usage logs."""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class WaterSource(Base, TimestampMixin):
    """Borewell, canal, rainwater harvesting tank, municipality line, etc."""
    __tablename__ = "water_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # borewell | canal | rainwater | municipal | pond | river
    capacity_liters: Mapped[Optional[float]] = mapped_column(Float)
    depth_meters: Mapped[Optional[float]] = mapped_column(Float)       # for borewells
    pump_hp: Mapped[Optional[float]] = mapped_column(Float)
    location_description: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    usage_logs: Mapped[List["WaterUsageLog"]] = relationship(
        "WaterUsageLog", back_populates="source"
    )
    quality_tests: Mapped[List["WaterQualityTest"]] = relationship(
        "WaterQualityTest", back_populates="source"
    )


class WaterStorageTank(Base, TimestampMixin):
    """Overhead tanks, sumps, or field reservoirs."""
    __tablename__ = "water_storage_tanks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tank_type: Mapped[str] = mapped_column(String(50))  # overhead | sump | field_reservoir
    capacity_liters: Mapped[float] = mapped_column(Float, default=0)
    current_level_liters: Mapped[float] = mapped_column(Float, default=0)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("water_sources.id"))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    has_sensor: Mapped[bool] = mapped_column(Boolean, default=False)
    sensor_device_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sensor_devices.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class IrrigationZone(Base, TimestampMixin):
    """Named irrigation zone — greenhouse block, field plot, nursery bed, etc."""
    __tablename__ = "irrigation_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(50))  # drip | sprinkler | flood | mist | manual
    area_sq_meters: Mapped[Optional[float]] = mapped_column(Float)
    crop_or_section: Mapped[Optional[str]] = mapped_column(String(100))
    tank_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("water_storage_tanks.id"))
    flow_rate_lpm: Mapped[Optional[float]] = mapped_column(Float)    # litres per minute
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    irrigation_logs: Mapped[List["IrrigationLog"]] = relationship(
        "IrrigationLog", back_populates="zone"
    )


class IrrigationLog(Base, TimestampMixin):
    """Each irrigation event per zone."""
    __tablename__ = "irrigation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[int] = mapped_column(Integer, ForeignKey("irrigation_zones.id"), nullable=False, index=True)
    irrigation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[float] = mapped_column(Float, default=0)
    volume_liters: Mapped[float] = mapped_column(Float, default=0)
    method: Mapped[Optional[str]] = mapped_column(String(50))  # drip | sprinkler | manual
    trigger: Mapped[str] = mapped_column(String(30), default="manual")  # manual | scheduled | sensor
    fertilizer_injected: Mapped[bool] = mapped_column(Boolean, default=False)
    fertilizer_type: Mapped[Optional[str]] = mapped_column(String(100))
    fertilizer_dose_ml: Mapped[Optional[float]] = mapped_column(Float)
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    zone: Mapped["IrrigationZone"] = relationship("IrrigationZone", back_populates="irrigation_logs")


class WaterUsageLog(Base, TimestampMixin):
    """Daily water drawn from a source."""
    __tablename__ = "water_usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("water_sources.id"), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    volume_liters: Mapped[float] = mapped_column(Float, default=0)
    purpose: Mapped[Optional[str]] = mapped_column(String(100))
    # irrigation | drinking | processing | cleaning | aquaculture
    energy_kwh: Mapped[Optional[float]] = mapped_column(Float)   # pumping energy
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    source: Mapped["WaterSource"] = relationship("WaterSource", back_populates="usage_logs")


class WaterQualityTest(Base, TimestampMixin):
    """Periodic water quality measurement for a source."""
    __tablename__ = "water_quality_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("water_sources.id"), nullable=False, index=True)
    test_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    ph: Mapped[Optional[float]] = mapped_column(Float)
    tds_ppm: Mapped[Optional[float]] = mapped_column(Float)        # Total Dissolved Solids
    ec_ms_cm: Mapped[Optional[float]] = mapped_column(Float)       # Electrical Conductivity
    turbidity_ntu: Mapped[Optional[float]] = mapped_column(Float)
    hardness_ppm: Mapped[Optional[float]] = mapped_column(Float)
    chlorine_ppm: Mapped[Optional[float]] = mapped_column(Float)
    nitrate_ppm: Mapped[Optional[float]] = mapped_column(Float)
    coliform_detected: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_potable: Mapped[Optional[bool]] = mapped_column(Boolean)    # suitable for drinking/livestock
    lab_name: Mapped[Optional[str]] = mapped_column(String(100))
    tested_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    source: Mapped["WaterSource"] = relationship("WaterSource", back_populates="quality_tests")
