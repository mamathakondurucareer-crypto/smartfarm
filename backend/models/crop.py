"""Crop management: greenhouse, vertical farm, field crops, activities, harvests, disease tracking."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin, SoftDeleteMixin


class GreenhouseCrop(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "greenhouse_crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    greenhouse_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 or 2
    crop_name: Mapped[str] = mapped_column(String(50), nullable=False)
    variety: Mapped[Optional[str]] = mapped_column(String(50))
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_harvest_start: Mapped[Optional[date]] = mapped_column(Date)
    expected_harvest_end: Mapped[Optional[date]] = mapped_column(Date)
    growth_stage: Mapped[str] = mapped_column(String(30), default="seedling")
    bed_number: Mapped[Optional[str]] = mapped_column(String(10))
    area_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    plant_count: Mapped[int] = mapped_column(Integer, default=0)
    plant_spacing_cm: Mapped[float] = mapped_column(Float, default=40)
    health_score: Mapped[float] = mapped_column(Float, default=100)  # 0-100
    target_yield_kg: Mapped[float] = mapped_column(Float, default=0)
    actual_yield_kg: Mapped[float] = mapped_column(Float, default=0)
    irrigation_type: Mapped[str] = mapped_column(String(20), default="drip")
    substrate: Mapped[str] = mapped_column(String(30), default="soil")  # soil, cocopeat, hydroponic
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    activities: Mapped[List["CropActivity"]] = relationship("CropActivity", back_populates="greenhouse_crop", foreign_keys="CropActivity.greenhouse_crop_id")
    harvests: Mapped[List["CropHarvest"]] = relationship("CropHarvest", back_populates="greenhouse_crop", foreign_keys="CropHarvest.greenhouse_crop_id")
    diseases: Mapped[List["CropDisease"]] = relationship("CropDisease", back_populates="greenhouse_crop", foreign_keys="CropDisease.greenhouse_crop_id")


class VerticalFarmBatch(Base, TimestampMixin):
    __tablename__ = "vertical_farm_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    crop_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tier: Mapped[str] = mapped_column(String(10), nullable=False)  # 1, 2, 3-4, etc.
    seeding_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date)
    cycle_days: Mapped[int] = mapped_column(Integer, nullable=False)  # total cycle length
    current_day: Mapped[int] = mapped_column(Integer, default=0)
    tray_count: Mapped[int] = mapped_column(Integer, nullable=False)
    health_score: Mapped[float] = mapped_column(Float, default=100)
    nutrient_ec: Mapped[float] = mapped_column(Float, default=2.0)  # mS/cm
    nutrient_ph: Mapped[float] = mapped_column(Float, default=6.0)
    led_hours_per_day: Mapped[float] = mapped_column(Float, default=16)
    expected_yield_kg: Mapped[float] = mapped_column(Float, default=0)
    actual_yield_kg: Mapped[float] = mapped_column(Float, default=0)
    seed_cost: Mapped[float] = mapped_column(Float, default=0)
    nutrient_cost: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="growing")
    notes: Mapped[Optional[str]] = mapped_column(Text)


class FieldCrop(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "field_crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    crop_name: Mapped[str] = mapped_column(String(50), nullable=False)  # turmeric, ginger
    variety: Mapped[Optional[str]] = mapped_column(String(50))
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date)
    area_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    seed_quantity_kg: Mapped[float] = mapped_column(Float, default=0)
    seed_cost: Mapped[float] = mapped_column(Float, default=0)
    growth_stage: Mapped[str] = mapped_column(String(30), default="planted")
    health_score: Mapped[float] = mapped_column(Float, default=100)
    target_yield_kg: Mapped[float] = mapped_column(Float, default=0)
    actual_yield_kg: Mapped[float] = mapped_column(Float, default=0)
    irrigation_source: Mapped[str] = mapped_column(String(30), default="pond_water")
    fertilizer_plan: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[Optional[str]] = mapped_column(Text)


class CropActivity(Base, TimestampMixin):
    __tablename__ = "crop_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    greenhouse_crop_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("greenhouse_crops.id"))
    field_crop_id: Mapped[Optional[int]] = mapped_column(Integer)
    activity_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: planting, transplanting, pruning, staking, fertigation, spraying, weeding, mulching, harvesting
    description: Mapped[str] = mapped_column(Text, nullable=False)
    chemical_used: Mapped[Optional[str]] = mapped_column(String(100))
    chemical_quantity: Mapped[Optional[float]] = mapped_column(Float)
    chemical_unit: Mapped[Optional[str]] = mapped_column(String(10))
    labour_hours: Mapped[float] = mapped_column(Float, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0)
    method: Mapped[str] = mapped_column(String(20), default="manual")  # manual, drone, auto
    performed_by: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    greenhouse_crop: Mapped[Optional["GreenhouseCrop"]] = relationship("GreenhouseCrop", back_populates="activities")


class CropHarvest(Base, TimestampMixin):
    __tablename__ = "crop_harvests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    greenhouse_crop_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("greenhouse_crops.id"))
    field_crop_id: Mapped[Optional[int]] = mapped_column(Integer)
    vf_batch_id: Mapped[Optional[int]] = mapped_column(Integer)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    crop_name: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(10), default="A")
    wastage_kg: Mapped[float] = mapped_column(Float, default=0)
    packaging_type: Mapped[Optional[str]] = mapped_column(String(30))
    cold_stored: Mapped[bool] = mapped_column(Boolean, default=False)
    destination: Mapped[Optional[str]] = mapped_column(String(50))
    sale_price_per_kg: Mapped[float] = mapped_column(Float, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    greenhouse_crop: Mapped[Optional["GreenhouseCrop"]] = relationship("GreenhouseCrop", back_populates="harvests")


class CropDisease(Base, TimestampMixin):
    __tablename__ = "crop_diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    greenhouse_crop_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("greenhouse_crops.id"))
    field_crop_id: Mapped[Optional[int]] = mapped_column(Integer)
    detected_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    disease_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pathogen_type: Mapped[str] = mapped_column(String(30))  # fungal, bacterial, viral, pest, nutritional
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # mild, moderate, severe
    affected_area_pct: Mapped[float] = mapped_column(Float, default=0)
    detection_method: Mapped[str] = mapped_column(String(20), default="ai_camera")  # ai_camera, manual, drone
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    treatment_applied: Mapped[Optional[str]] = mapped_column(Text)
    treatment_date: Mapped[Optional[date]] = mapped_column(Date)
    treatment_cost: Mapped[float] = mapped_column(Float, default=0)
    outcome: Mapped[str] = mapped_column(String(20), default="pending")  # pending, resolved, escalated, crop_loss
    yield_impact_pct: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    greenhouse_crop: Mapped[Optional["GreenhouseCrop"]] = relationship("GreenhouseCrop", back_populates="diseases")
