"""IoT sensor devices, readings, and alert management."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class SensorDevice(Base, TimestampMixin):
    __tablename__ = "sensor_devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: soil, water_quality, weather, environmental, poultry, camera, level
    location: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str] = mapped_column(String(30), nullable=False)  # pond_p1, gh1, poultry, reservoir, etc.
    protocol: Mapped[str] = mapped_column(String(20), default="lorawan")  # lorawan, wifi, modbus
    model: Mapped[Optional[str]] = mapped_column(String(50))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(50))
    battery_level: Mapped[Optional[float]] = mapped_column(Float)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(20))
    calibration_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_reading_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="online")  # online, offline, maintenance, error
    notes: Mapped[Optional[str]] = mapped_column(Text)

    readings: Mapped[List["SensorReading"]] = relationship("SensorReading", back_populates="device")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sensor_devices.id"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    parameter: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    # Parameters: dissolved_oxygen, ph, water_temp, ammonia, soil_moisture, soil_temp, soil_ec,
    #             air_temp, humidity, co2, light_par, wind_speed, rainfall, solar_radiation,
    #             water_level, feed_level, egg_count, ammonia_air
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(15), nullable=False)

    device: Mapped["SensorDevice"] = relationship("SensorDevice", back_populates="readings")


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, warning, info
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    # Categories: water_quality, climate, equipment, disease, inventory, financial, security
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_device_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sensor_devices.id"))
    source_system: Mapped[str] = mapped_column(String(30), nullable=False)
    triggered_value: Mapped[Optional[float]] = mapped_column(Float)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float)
    zone: Mapped[Optional[str]] = mapped_column(String(30))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(50))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    auto_action_taken: Mapped[Optional[str]] = mapped_column(Text)


class SensorCalibrationLog(Base, TimestampMixin):
    """Calibration record for an IoT sensor device."""
    __tablename__ = "sensor_calibration_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(Integer, ForeignKey("sensor_devices.id"), nullable=False, index=True)
    calibration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_calibration_due: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    variance_before: Mapped[Optional[float]] = mapped_column(Float)   # drift measured
    variance_after: Mapped[Optional[float]] = mapped_column(Float)    # after correction
    calibration_standard: Mapped[Optional[str]] = mapped_column(String(100))  # reference standard used
    technician: Mapped[str] = mapped_column(String(100), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class BatteryReplacementLog(Base, TimestampMixin):
    """Battery replacement record for sensor devices."""
    __tablename__ = "battery_replacement_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(Integer, ForeignKey("sensor_devices.id"), nullable=False, index=True)
    replacement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    battery_type: Mapped[Optional[str]] = mapped_column(String(50))
    next_replacement_due: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    replaced_by: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class CameraFirmwareLog(Base, TimestampMixin):
    """Firmware update log for camera / edge devices."""
    __tablename__ = "camera_firmware_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sensor_id: Mapped[int] = mapped_column(Integer, ForeignKey("sensor_devices.id"), nullable=False, index=True)
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    previous_version: Mapped[Optional[str]] = mapped_column(String(20))
    new_version: Mapped[str] = mapped_column(String(20), nullable=False)
    update_method: Mapped[Optional[str]] = mapped_column(String(50))  # OTA | manual | USB
    updated_by: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
