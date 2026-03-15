"""Incident tracking: disease outbreaks, equipment failures, weather events, maintenance schedules."""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    incident_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: disease_fish, disease_poultry, disease_crop, equipment_failure, power_outage,
    #        water_quality, flood, cyclone, drought, theft, fire, pest_outbreak, chemical_spill
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high, critical
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reported_by: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_system: Mapped[str] = mapped_column(String(30), nullable=False)
    affected_quantity: Mapped[Optional[str]] = mapped_column(String(50))
    estimated_loss: Mapped[float] = mapped_column(Float, default=0)
    actual_loss: Mapped[float] = mapped_column(Float, default=0)
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    detection_method: Mapped[str] = mapped_column(String(30), default="manual")
    # Methods: manual, sensor, ai_camera, drone, routine_check
    insurance_claim: Mapped[bool] = mapped_column(Boolean, default=False)
    insurance_claim_amount: Mapped[float] = mapped_column(Float, default=0)
    insurance_status: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open")
    # Status: open, investigating, containment, resolved, closed
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_summary: Mapped[Optional[str]] = mapped_column(Text)
    preventive_measures: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    actions: Mapped[List["IncidentAction"]] = relationship("IncidentAction", back_populates="incident")


class IncidentAction(Base, TimestampMixin):
    __tablename__ = "incident_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(Integer, ForeignKey("incidents.id"), nullable=False)
    action_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: quarantine, treatment, repair, replacement, evacuation, chemical_application,
    #        water_change, aeration, ventilation, vaccination, culling, harvesting
    description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by: Mapped[str] = mapped_column(String(50), nullable=False)
    materials_used: Mapped[Optional[str]] = mapped_column(Text)
    cost: Mapped[float] = mapped_column(Float, default=0)
    result: Mapped[str] = mapped_column(String(20), default="pending")
    # Results: effective, partially_effective, ineffective, pending
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="actions")


class MaintenanceSchedule(Base, TimestampMixin):
    __tablename__ = "maintenance_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment: Mapped[str] = mapped_column(String(100), nullable=False)
    equipment_location: Mapped[str] = mapped_column(String(50), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # Types: preventive, corrective, calibration, cleaning, lubrication, replacement
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    # Frequency: daily, weekly, monthly, quarterly, semi_annual, annual, as_needed
    last_performed: Mapped[Optional[date]] = mapped_column(Date)
    next_due: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(50))
    estimated_duration_hours: Mapped[float] = mapped_column(Float, default=1)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)
    spare_parts_needed: Mapped[Optional[str]] = mapped_column(Text)
    checklist: Mapped[Optional[str]] = mapped_column(Text)  # JSON checklist
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    # Status: scheduled, in_progress, completed, overdue, skipped
    completion_notes: Mapped[Optional[str]] = mapped_column(Text)
    actual_cost: Mapped[float] = mapped_column(Float, default=0)
