"""Production tracking: batches, processing, packaging, quality checks, stock ledger."""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class ProductionBatch(Base, TimestampMixin):
    __tablename__ = "production_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    production_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    # Categories: fresh_fish, live_fish, fresh_vegetables, leafy_greens, eggs, honey,
    #             dried_turmeric, ginger_paste, seedlings, vermicompost
    source: Mapped[str] = mapped_column(String(30), nullable=False)  # pond_p1, gh1, vf, poultry, etc.
    raw_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    raw_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    processed_quantity: Mapped[float] = mapped_column(Float, default=0)
    wastage_quantity: Mapped[float] = mapped_column(Float, default=0)
    wastage_pct: Mapped[float] = mapped_column(Float, default=0)
    final_quantity: Mapped[float] = mapped_column(Float, default=0)
    final_unit: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[str] = mapped_column(String(10), default="A")
    cost_of_production: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="produced")
    # Status: produced, processing, packaged, in_cold_storage, dispatched, sold
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ProcessingLog(Base, TimestampMixin):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("production_batches.id"), nullable=False)
    process_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: cleaning, washing, grading, sorting, cutting, drying, curing, grinding, mixing
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    input_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    output_quantity: Mapped[float] = mapped_column(Float, default=0)
    wastage: Mapped[float] = mapped_column(Float, default=0)
    equipment_used: Mapped[Optional[str]] = mapped_column(String(100))
    performed_by: Mapped[Optional[str]] = mapped_column(String(50))
    temperature: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class PackagingLog(Base, TimestampMixin):
    __tablename__ = "packaging_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("production_batches.id"), nullable=False)
    packaging_date: Mapped[date] = mapped_column(Date, nullable=False)
    packaging_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: crate, box, tray_30, tray_6, bag_1kg, bag_5kg, carton, thermocol_box, live_tank
    quantity_packed: Mapped[float] = mapped_column(Float, nullable=False)
    units_packed: Mapped[int] = mapped_column(Integer, nullable=False)
    label_info: Mapped[Optional[str]] = mapped_column(Text)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    cold_stored: Mapped[bool] = mapped_column(Boolean, default=False)
    storage_temp: Mapped[Optional[float]] = mapped_column(Float)
    packaging_cost: Mapped[float] = mapped_column(Float, default=0)
    performed_by: Mapped[Optional[str]] = mapped_column(String(50))


class QualityCheck(Base, TimestampMixin):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(Integer, ForeignKey("production_batches.id"), nullable=False)
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    check_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: visual, weight, freshness, lab_test, pesticide_residue, moisture, microbial
    parameter: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_value: Mapped[Optional[str]] = mapped_column(String(50))
    actual_value: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)  # pass, fail, borderline
    checked_by: Mapped[str] = mapped_column(String(50), nullable=False)
    corrective_action: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)


class StockLedger(Base, TimestampMixin):
    __tablename__ = "stock_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    current_stock: Mapped[float] = mapped_column(Float, default=0)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    location: Mapped[str] = mapped_column(String(30), default="packhouse")
    # Locations: packhouse, cold_room, loading_dock, pond_side, greenhouse, field
    avg_cost_per_unit: Mapped[float] = mapped_column(Float, default=0)
    total_value: Mapped[float] = mapped_column(Float, default=0)
    last_in_date: Mapped[Optional[date]] = mapped_column(Date)
    last_out_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)


class StockMovement(Base, TimestampMixin):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Types: production_in, harvest_in, purchase_in, sale_out, shipment_out, wastage_out,
    #        transfer, adjustment, return_in, sample_out
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    from_location: Mapped[Optional[str]] = mapped_column(String(30))
    to_location: Mapped[Optional[str]] = mapped_column(String(30))
    reference_type: Mapped[Optional[str]] = mapped_column(String(30))
    reference_id: Mapped[Optional[int]] = mapped_column(Integer)
    batch_code: Mapped[Optional[str]] = mapped_column(String(20))
    unit_cost: Mapped[float] = mapped_column(Float, default=0)
    total_value: Mapped[float] = mapped_column(Float, default=0)
    performed_by: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)
