"""Poultry, duck, and apiculture management models."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class PoultryFlock(Base, TimestampMixin):
    __tablename__ = "poultry_flocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flock_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    breed: Mapped[str] = mapped_column(String(50), nullable=False)  # BV-300, Lohmann Brown
    flock_type: Mapped[str] = mapped_column(String(20), nullable=False)  # layer, broiler
    arrival_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    age_weeks: Mapped[int] = mapped_column(Integer, default=0)
    avg_weight_g: Mapped[float] = mapped_column(Float, default=0)
    lay_rate_pct: Mapped[float] = mapped_column(Float, default=0)
    peak_lay_pct: Mapped[float] = mapped_column(Float, default=0)
    total_eggs_produced: Mapped[int] = mapped_column(Integer, default=0)
    total_mortality: Mapped[int] = mapped_column(Integer, default=0)
    vaccination_status: Mapped[Optional[str]] = mapped_column(Text)  # JSON: list of vaccinations
    status: Mapped[str] = mapped_column(String(20), default="laying")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    egg_collections: Mapped[List["EggCollection"]] = relationship("EggCollection", back_populates="flock")
    feed_logs: Mapped[List["PoultryFeedLog"]] = relationship("PoultryFeedLog", back_populates="flock")
    health_logs: Mapped[List["PoultryHealthLog"]] = relationship("PoultryHealthLog", back_populates="flock")


class EggCollection(Base, TimestampMixin):
    __tablename__ = "egg_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flock_id: Mapped[int] = mapped_column(Integer, ForeignKey("poultry_flocks.id"), nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_eggs: Mapped[int] = mapped_column(Integer, nullable=False)
    broken_eggs: Mapped[int] = mapped_column(Integer, default=0)
    dirty_eggs: Mapped[int] = mapped_column(Integer, default=0)
    grade_a: Mapped[int] = mapped_column(Integer, default=0)
    grade_b: Mapped[int] = mapped_column(Integer, default=0)
    grade_c: Mapped[int] = mapped_column(Integer, default=0)
    avg_weight_g: Mapped[float] = mapped_column(Float, default=58)
    eggs_washed: Mapped[int] = mapped_column(Integer, default=0)
    eggs_packed: Mapped[int] = mapped_column(Integer, default=0)
    eggs_sold: Mapped[int] = mapped_column(Integer, default=0)
    sale_price_per_egg: Mapped[float] = mapped_column(Float, default=8.0)
    revenue: Mapped[float] = mapped_column(Float, default=0)
    collection_method: Mapped[str] = mapped_column(String(20), default="auto_belt")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    flock: Mapped["PoultryFlock"] = relationship("PoultryFlock", back_populates="egg_collections")


class PoultryFeedLog(Base, TimestampMixin):
    __tablename__ = "poultry_feed_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flock_id: Mapped[int] = mapped_column(Integer, ForeignKey("poultry_flocks.id"), nullable=False)
    feed_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    feed_type: Mapped[str] = mapped_column(String(50), nullable=False)  # layer_mash, pre_lay, grower
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    cost_per_kg: Mapped[float] = mapped_column(Float, default=0)
    brand: Mapped[Optional[str]] = mapped_column(String(50))
    water_consumed_liters: Mapped[float] = mapped_column(Float, default=0)
    feed_per_bird_g: Mapped[float] = mapped_column(Float, default=0)
    method: Mapped[str] = mapped_column(String(20), default="auto")

    flock: Mapped["PoultryFlock"] = relationship("PoultryFlock", back_populates="feed_logs")


class PoultryHealthLog(Base, TimestampMixin):
    __tablename__ = "poultry_health_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flock_id: Mapped[int] = mapped_column(Integer, ForeignKey("poultry_flocks.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mortality_count: Mapped[int] = mapped_column(Integer, default=0)
    mortality_cause: Mapped[Optional[str]] = mapped_column(String(50))
    culled_count: Mapped[int] = mapped_column(Integer, default=0)
    sick_count: Mapped[int] = mapped_column(Integer, default=0)
    symptoms: Mapped[Optional[str]] = mapped_column(Text)
    treatment: Mapped[Optional[str]] = mapped_column(Text)
    vaccination_given: Mapped[Optional[str]] = mapped_column(String(100))
    vet_visit: Mapped[bool] = mapped_column(Boolean, default=False)
    shed_temp: Mapped[Optional[float]] = mapped_column(Float)
    shed_humidity: Mapped[Optional[float]] = mapped_column(Float)
    ammonia_ppm: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    flock: Mapped["PoultryFlock"] = relationship("PoultryFlock", back_populates="health_logs")


class DuckFlock(Base, TimestampMixin):
    __tablename__ = "duck_flocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flock_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    breed: Mapped[str] = mapped_column(String(50), nullable=False)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    primary_purpose: Mapped[str] = mapped_column(String(30), default="pest_control")
    deployment_area: Mapped[Optional[str]] = mapped_column(String(100))
    daily_eggs_avg: Mapped[float] = mapped_column(Float, default=0)
    eggs_today: Mapped[int] = mapped_column(Integer, default=0)
    total_eggs: Mapped[int] = mapped_column(Integer, default=0)
    pest_control_rating: Mapped[str] = mapped_column(String(20), default="high")
    notes: Mapped[Optional[str]] = mapped_column(Text)


class BeeHive(Base, TimestampMixin):
    __tablename__ = "bee_hives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hive_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    hive_type: Mapped[str] = mapped_column(String(30), default="langstroth")
    species: Mapped[str] = mapped_column(String(50), default="Apis mellifera")
    installation_date: Mapped[date] = mapped_column(Date, nullable=False)
    location_description: Mapped[Optional[str]] = mapped_column(String(100))
    queen_status: Mapped[str] = mapped_column(String(20), default="present")
    colony_strength: Mapped[str] = mapped_column(String(20), default="strong")
    frames_with_brood: Mapped[int] = mapped_column(Integer, default=0)
    frames_with_honey: Mapped[int] = mapped_column(Integer, default=0)
    last_inspection_date: Mapped[Optional[date]] = mapped_column(Date)
    disease_status: Mapped[str] = mapped_column(String(20), default="healthy")
    total_honey_harvested_kg: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[Optional[str]] = mapped_column(Text)

    honey_harvests: Mapped[List["HoneyHarvest"]] = relationship("HoneyHarvest", back_populates="hive")


class HoneyHarvest(Base, TimestampMixin):
    __tablename__ = "honey_harvests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hive_id: Mapped[int] = mapped_column(Integer, ForeignKey("bee_hives.id"), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    beeswax_kg: Mapped[float] = mapped_column(Float, default=0)
    propolis_g: Mapped[float] = mapped_column(Float, default=0)
    quality_grade: Mapped[str] = mapped_column(String(10), default="A")
    moisture_pct: Mapped[Optional[float]] = mapped_column(Float)
    sale_price_per_kg: Mapped[float] = mapped_column(Float, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0)

    hive: Mapped["BeeHive"] = relationship("BeeHive", back_populates="honey_harvests")
