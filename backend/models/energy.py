"""Solar & energy management — panels, inverters, generation, consumption, grid events."""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class SolarArray(Base, TimestampMixin):
    """A group of solar panels (string/array) on the farm."""
    __tablename__ = "solar_arrays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    panel_count: Mapped[int] = mapped_column(Integer, default=0)
    panel_wattage_wp: Mapped[float] = mapped_column(Float, default=0)  # watts-peak per panel
    total_capacity_kwp: Mapped[float] = mapped_column(Float, default=0)  # computed: count × wattage/1000
    tilt_degrees: Mapped[Optional[float]] = mapped_column(Float)
    azimuth_degrees: Mapped[Optional[float]] = mapped_column(Float)
    commissioned_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    generation_logs: Mapped[List["EnergyGenerationLog"]] = relationship(
        "EnergyGenerationLog", back_populates="solar_array"
    )


class Inverter(Base, TimestampMixin):
    """Solar inverter or grid-tie inverter."""
    __tablename__ = "inverters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    solar_array_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("solar_arrays.id"))
    make: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    rated_kva: Mapped[float] = mapped_column(Float, default=0)
    inverter_type: Mapped[str] = mapped_column(String(50), default="grid_tie")
    # grid_tie | off_grid | hybrid
    installation_date: Mapped[Optional[date]] = mapped_column(Date)
    last_service_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class EnergyGenerationLog(Base, TimestampMixin):
    """Daily solar generation reading per array."""
    __tablename__ = "energy_generation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solar_array_id: Mapped[int] = mapped_column(Integer, ForeignKey("solar_arrays.id"), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    units_generated_kwh: Mapped[float] = mapped_column(Float, default=0)
    peak_power_kw: Mapped[Optional[float]] = mapped_column(Float)
    sunshine_hours: Mapped[Optional[float]] = mapped_column(Float)
    inverter_efficiency_pct: Mapped[Optional[float]] = mapped_column(Float)
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    solar_array: Mapped["SolarArray"] = relationship("SolarArray", back_populates="generation_logs")


class EnergyConsumptionLog(Base, TimestampMixin):
    """Daily or section-level energy consumption."""
    __tablename__ = "energy_consumption_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(100), nullable=False)
    # greenhouse | aquaculture | packhouse | irrigation | cold_storage | office | total
    units_consumed_kwh: Mapped[float] = mapped_column(Float, default=0)
    source: Mapped[str] = mapped_column(String(30), default="solar")  # solar | grid | diesel | battery
    tariff_per_kwh: Mapped[Optional[float]] = mapped_column(Float)
    cost: Mapped[Optional[float]] = mapped_column(Float)
    meter_reading_start: Mapped[Optional[float]] = mapped_column(Float)
    meter_reading_end: Mapped[Optional[float]] = mapped_column(Float)
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class BatteryBank(Base, TimestampMixin):
    """Battery storage bank for off-grid / hybrid systems."""
    __tablename__ = "battery_banks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    battery_type: Mapped[str] = mapped_column(String(50))  # lithium | lead_acid | gel
    capacity_kwh: Mapped[float] = mapped_column(Float, default=0)
    current_soc_pct: Mapped[float] = mapped_column(Float, default=100)  # State of Charge
    cycles_completed: Mapped[int] = mapped_column(Integer, default=0)
    commissioned_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class GridEvent(Base, TimestampMixin):
    """Grid outage or supply fluctuation events."""
    __tablename__ = "grid_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50))  # outage | low_voltage | surge | scheduled_cut
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[Optional[float]] = mapped_column(Float)
    affected_sections: Mapped[Optional[str]] = mapped_column(Text)  # comma-separated
    backup_used: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_type: Mapped[Optional[str]] = mapped_column(String(50))  # battery | diesel_gen | none
    reported_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
