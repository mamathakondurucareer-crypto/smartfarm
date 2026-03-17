"""QA & Traceability models — lot tracking, quality tests, quarantine."""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, Boolean, Text, ForeignKey, DateTime
from backend.models.base import Base, TimestampMixin

class ProductLot(Base, TimestampMixin):
    __tablename__ = "product_lots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False)  # fish/eggs/vegetables/honey/seedlings/feed
    source_module: Mapped[str] = mapped_column(String(50))  # aquaculture/poultry/greenhouse/etc.
    source_id: Mapped[Optional[str]] = mapped_column(String(50))  # pond_id or batch_id
    produced_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(String(20), default="kg")  # kg/dozen/litres/units
    harvest_team: Mapped[Optional[str]] = mapped_column(String(100))
    qr_code: Mapped[Optional[str]] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/quarantine/released/rejected
    notes: Mapped[Optional[str]] = mapped_column(Text)

    quality_tests: Mapped[List["QualityTest"]] = relationship("QualityTest", back_populates="lot")
    quarantine_records: Mapped[List["QAQuarantine"]] = relationship("QAQuarantine", back_populates="lot")

class QualityTest(Base, TimestampMixin):
    __tablename__ = "quality_tests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_lots.id"), nullable=False)
    test_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # test_type: mrl_check/brix/salmonella/eggshell_strength/curcumin_pct/honey_moisture/honey_hmf/aflatoxin/protein_pct/visual/weight
    test_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    result_value: Mapped[Optional[float]] = mapped_column(Float)
    result_text: Mapped[Optional[str]] = mapped_column(String(200))
    passed: Mapped[bool] = mapped_column(Boolean, default=True)
    tester: Mapped[str] = mapped_column(String(100), nullable=False)
    lab: Mapped[Optional[str]] = mapped_column(String(100))  # internal / ICAR-CIFA / external lab
    notes: Mapped[Optional[str]] = mapped_column(Text)

    lot: Mapped["ProductLot"] = relationship("ProductLot", back_populates="quality_tests")

class QAQuarantine(Base, TimestampMixin):
    __tablename__ = "qa_quarantine"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_lots.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    quarantine_date: Mapped[date] = mapped_column(Date, nullable=False)
    resolved_date: Mapped[Optional[date]] = mapped_column(Date)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100))
    resolution: Mapped[Optional[str]] = mapped_column(Text)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    lot: Mapped["ProductLot"] = relationship("ProductLot", back_populates="quarantine_records")
