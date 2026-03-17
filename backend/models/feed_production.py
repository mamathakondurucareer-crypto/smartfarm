"""Feed production models: BSF, Azolla, Duckweed, Feed Mill batches, Feed Inventory."""
import enum
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, Boolean, Text, ForeignKey, DateTime, Enum as SAEnum
from backend.models.base import Base, TimestampMixin, SoftDeleteMixin

class BSFColony(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "bsf_colonies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    colony_stage: Mapped[str] = mapped_column(String(30), default="egg")  # egg/larvae/prepupae/pupae
    substrate_type: Mapped[str] = mapped_column(String(50), default="kitchen_waste")
    daily_yield_kg: Mapped[float] = mapped_column(Float, default=0.0)
    moisture_pct: Mapped[float] = mapped_column(Float, default=60.0)
    larvae_age_days: Mapped[int] = mapped_column(Integer, default=0)
    colony_health: Mapped[str] = mapped_column(String(20), default="good")  # good/fair/poor
    notes: Mapped[Optional[str]] = mapped_column(Text)

class AzollaLog(Base, TimestampMixin):
    __tablename__ = "azolla_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bed_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    harvest_kg: Mapped[float] = mapped_column(Float, default=0.0)
    moisture_pct: Mapped[float] = mapped_column(Float, default=90.0)
    protein_pct: Mapped[float] = mapped_column(Float, default=25.0)
    area_sqm: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)

class DuckweedLog(Base, TimestampMixin):
    __tablename__ = "duckweed_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pond_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    yield_kg: Mapped[float] = mapped_column(Float, default=0.0)
    water_tds: Mapped[float] = mapped_column(Float, default=0.0)
    ph: Mapped[float] = mapped_column(Float, default=7.0)
    allocated_to: Mapped[str] = mapped_column(String(50), default="fish")  # fish/poultry/poultry_ducks
    notes: Mapped[Optional[str]] = mapped_column(Text)

class FeedMillBatch(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "feed_mill_batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    formulation: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "BSF30-Azolla20-Soya50"
    date_produced: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity_kg: Mapped[float] = mapped_column(Float, default=0.0)
    moisture_pct: Mapped[float] = mapped_column(Float, default=12.0)
    protein_pct: Mapped[float] = mapped_column(Float, default=28.0)
    aflatoxin_ppb: Mapped[float] = mapped_column(Float, default=0.0)
    pellet_durability_pct: Mapped[float] = mapped_column(Float, default=98.0)
    target_species: Mapped[str] = mapped_column(String(50), default="fish")
    passed_qa: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text)

class FeedInventory(Base, TimestampMixin):
    __tablename__ = "feed_inventory"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feed_type: Mapped[str] = mapped_column(String(50), nullable=False)  # on_farm_bsf, on_farm_azolla, purchased_pellet, etc.
    quantity_kg: Mapped[float] = mapped_column(Float, default=0.0)
    unit_cost_per_kg: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(100))  # supplier name or "on-farm"
    received_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    batch_code: Mapped[Optional[str]] = mapped_column(String(30))
    notes: Mapped[Optional[str]] = mapped_column(Text)
