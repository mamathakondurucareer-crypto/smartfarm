"""Aquaculture management: ponds, fish batches, feeding, water quality, harvests, crab fattening."""

from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin, SoftDeleteMixin


class Pond(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "ponds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pond_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # P1, P2, etc.
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    pond_type: Mapped[str] = mapped_column(String(30), nullable=False)  # murrel, imc_polyculture, nursery, crab
    length_m: Mapped[float] = mapped_column(Float, nullable=False)
    width_m: Mapped[float] = mapped_column(Float, nullable=False)
    depth_m: Mapped[float] = mapped_column(Float, nullable=False)
    area_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    volume_liters: Mapped[float] = mapped_column(Float, nullable=False)
    lining_type: Mapped[str] = mapped_column(String(30), default="earthen")  # earthen, hdpe, concrete
    num_aerators: Mapped[int] = mapped_column(Integer, default=2)
    has_auto_feeder: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, draining, maintenance, fallow
    notes: Mapped[Optional[str]] = mapped_column(Text)

    fish_batches: Mapped[List["FishBatch"]] = relationship("FishBatch", back_populates="pond")
    feed_logs: Mapped[List["FeedLog"]] = relationship("FeedLog", back_populates="pond")
    water_logs: Mapped[List["WaterQualityLog"]] = relationship("WaterQualityLog", back_populates="pond")
    harvests: Mapped[List["FishHarvest"]] = relationship("FishHarvest", back_populates="pond")

    @property
    def area_hectares(self) -> float:
        return self.area_sqm / 10000


class FishBatch(Base, TimestampMixin):
    __tablename__ = "fish_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pond_id: Mapped[int] = mapped_column(Integer, ForeignKey("ponds.id"), nullable=False)
    batch_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=False)  # murrel, rohu, catla, grass_carp, common_carp
    variety: Mapped[Optional[str]] = mapped_column(String(50))
    stocking_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_avg_weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    current_avg_weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date)
    target_weight_g: Mapped[float] = mapped_column(Float, default=1000)
    source_hatchery: Mapped[Optional[str]] = mapped_column(String(100))
    cost_per_fingerling: Mapped[float] = mapped_column(Float, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0)
    mortality_count: Mapped[int] = mapped_column(Integer, default=0)
    fcr: Mapped[float] = mapped_column(Float, default=0)  # feed conversion ratio
    status: Mapped[str] = mapped_column(String(20), default="growing")  # growing, harvesting, completed
    notes: Mapped[Optional[str]] = mapped_column(Text)

    pond: Mapped["Pond"] = relationship("Pond", back_populates="fish_batches")

    @property
    def mortality_pct(self) -> float:
        if self.initial_count == 0:
            return 0
        return (self.mortality_count / self.initial_count) * 100

    @property
    def biomass_kg(self) -> float:
        return (self.current_count * self.current_avg_weight_g) / 1000

    @property
    def survival_rate(self) -> float:
        if self.initial_count == 0:
            return 0
        return (self.current_count / self.initial_count) * 100


class FeedLog(Base, TimestampMixin):
    __tablename__ = "feed_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pond_id: Mapped[int] = mapped_column(Integer, ForeignKey("ponds.id"), nullable=False)
    feed_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    feed_time: Mapped[str] = mapped_column(String(10), nullable=False)  # morning, noon, evening
    feed_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pellet_32, pellet_36, trash_fish, oil_cake
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(50))
    batch_number: Mapped[Optional[str]] = mapped_column(String(30))
    cost_per_kg: Mapped[float] = mapped_column(Float, default=0)
    method: Mapped[str] = mapped_column(String(20), default="auto")  # auto, manual, broadcast
    notes: Mapped[Optional[str]] = mapped_column(Text)

    pond: Mapped["Pond"] = relationship("Pond", back_populates="feed_logs")

    @property
    def total_cost(self) -> float:
        return self.quantity_kg * self.cost_per_kg


class WaterQualityLog(Base, TimestampMixin):
    __tablename__ = "water_quality_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pond_id: Mapped[int] = mapped_column(Integer, ForeignKey("ponds.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    dissolved_oxygen: Mapped[Optional[float]] = mapped_column(Float)  # mg/L
    ph: Mapped[Optional[float]] = mapped_column(Float)
    water_temperature: Mapped[Optional[float]] = mapped_column(Float)  # °C
    ammonia: Mapped[Optional[float]] = mapped_column(Float)  # mg/L
    nitrite: Mapped[Optional[float]] = mapped_column(Float)  # mg/L
    nitrate: Mapped[Optional[float]] = mapped_column(Float)  # mg/L
    turbidity: Mapped[Optional[float]] = mapped_column(Float)  # NTU
    alkalinity: Mapped[Optional[float]] = mapped_column(Float)  # mg/L CaCO3
    hardness: Mapped[Optional[float]] = mapped_column(Float)  # mg/L CaCO3
    transparency_cm: Mapped[Optional[float]] = mapped_column(Float)  # secchi disk
    source: Mapped[str] = mapped_column(String(20), default="sensor")  # sensor, manual, lab
    notes: Mapped[Optional[str]] = mapped_column(Text)

    pond: Mapped["Pond"] = relationship("Pond", back_populates="water_logs")


class FishHarvest(Base, TimestampMixin):
    __tablename__ = "fish_harvests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pond_id: Mapped[int] = mapped_column(Integer, ForeignKey("ponds.id"), nullable=False)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("fish_batches.id"), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    harvest_type: Mapped[str] = mapped_column(String(20), nullable=False)  # partial, full
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[str] = mapped_column(String(10), default="A")  # A, B, C
    sale_price_per_kg: Mapped[float] = mapped_column(Float, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0)
    buyer: Mapped[Optional[str]] = mapped_column(String(100))
    destination_market: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    pond: Mapped["Pond"] = relationship("Pond", back_populates="harvests")


class CrabBatch(Base, TimestampMixin):
    __tablename__ = "crab_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    stocking_date: Mapped[date] = mapped_column(Date, nullable=False)
    initial_count: Mapped[int] = mapped_column(Integer, nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False)
    initial_avg_weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    current_avg_weight_g: Mapped[float] = mapped_column(Float, nullable=False)
    target_weight_g: Mapped[float] = mapped_column(Float, default=600)
    expected_harvest_date: Mapped[Optional[date]] = mapped_column(Date)
    mortality_count: Mapped[int] = mapped_column(Integer, default=0)
    feed_type: Mapped[str] = mapped_column(String(50), default="trash_fish")
    total_feed_kg: Mapped[float] = mapped_column(Float, default=0)
    total_feed_cost: Mapped[float] = mapped_column(Float, default=0)
    harvest_kg: Mapped[float] = mapped_column(Float, default=0)
    harvest_revenue: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="fattening")  # fattening, harvested
    notes: Mapped[Optional[str]] = mapped_column(Text)
