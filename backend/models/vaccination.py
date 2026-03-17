"""Vaccination schedules, disease alerts, and treatment logs for all livestock."""

from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class VaccinationSchedule(Base, TimestampMixin):
    """Master vaccination protocol — which vaccine, for which species, at what intervals."""
    __tablename__ = "vaccination_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    species: Mapped[str] = mapped_column(String(50), nullable=False)  # poultry | fish | duck | cattle | goat
    vaccine_name: Mapped[str] = mapped_column(String(150), nullable=False)
    disease_target: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. Newcastle, Marek's
    dose_ml: Mapped[float] = mapped_column(Float, default=0)
    route: Mapped[str] = mapped_column(String(50))  # oral | injectable | ocular | nasal
    age_days_start: Mapped[Optional[int]] = mapped_column(Integer)   # earliest age for first dose
    repeat_interval_days: Mapped[Optional[int]] = mapped_column(Integer)  # 0 = one-time
    booster_required: Mapped[bool] = mapped_column(Boolean, default=False)
    withdrawal_period_days: Mapped[int] = mapped_column(Integer, default=0)  # meat/egg withdrawal
    notes: Mapped[Optional[str]] = mapped_column(Text)

    vaccination_records: Mapped[List["VaccinationRecord"]] = relationship(
        "VaccinationRecord", back_populates="schedule"
    )


class VaccinationRecord(Base, TimestampMixin):
    """Actual vaccination event applied to a batch/flock."""
    __tablename__ = "vaccination_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("vaccination_schedules.id"), nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    batch_or_flock_id: Mapped[int] = mapped_column(Integer, nullable=False)  # FK resolved at app layer
    batch_or_flock_ref: Mapped[str] = mapped_column(String(100), nullable=False)  # human-readable label
    vaccination_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    dose_given_ml: Mapped[float] = mapped_column(Float, default=0)
    animals_vaccinated: Mapped[int] = mapped_column(Integer, default=0)
    vaccinated_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    next_due_date: Mapped[Optional[date]] = mapped_column(Date)
    lot_number: Mapped[Optional[str]] = mapped_column(String(50))   # vaccine batch/lot
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    adverse_reactions: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    schedule: Mapped["VaccinationSchedule"] = relationship(
        "VaccinationSchedule", back_populates="vaccination_records"
    )


class DiseaseAlert(Base, TimestampMixin):
    """Suspected or confirmed disease outbreak record."""
    __tablename__ = "disease_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    batch_or_flock_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    disease_name: Mapped[str] = mapped_column(String(150), nullable=False)
    symptoms: Mapped[Optional[str]] = mapped_column(Text)
    affected_count: Mapped[int] = mapped_column(Integer, default=0)
    mortality_count: Mapped[int] = mapped_column(Integer, default=0)
    severity: Mapped[str] = mapped_column(String(20), default="moderate")  # low | moderate | high | critical
    status: Mapped[str] = mapped_column(String(30), default="suspected")  # suspected | confirmed | resolved | false_alarm
    lab_test_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    lab_result: Mapped[Optional[str]] = mapped_column(Text)
    quarantine_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    reported_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    treatment_logs: Mapped[List["TreatmentLog"]] = relationship(
        "TreatmentLog", back_populates="disease_alert"
    )


class TreatmentLog(Base, TimestampMixin):
    """Medication / treatment applied in response to a disease alert."""
    __tablename__ = "treatment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disease_alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("disease_alerts.id"), nullable=False)
    treatment_date: Mapped[date] = mapped_column(Date, nullable=False)
    drug_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)    # e.g. "5 mg/kg"
    route: Mapped[str] = mapped_column(String(50))                      # oral | injectable | topical
    animals_treated: Mapped[int] = mapped_column(Integer, default=0)
    duration_days: Mapped[int] = mapped_column(Integer, default=1)
    withdrawal_period_days: Mapped[int] = mapped_column(Integer, default=0)
    withdrawal_end_date: Mapped[Optional[date]] = mapped_column(Date)  # computed: treatment_date + withdrawal
    cost: Mapped[float] = mapped_column(Float, default=0)
    outcome: Mapped[Optional[str]] = mapped_column(String(50))  # improving | stable | worsening | recovered
    administered_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    vet_name: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    disease_alert: Mapped["DiseaseAlert"] = relationship(
        "DiseaseAlert", back_populates="treatment_logs"
    )


class MortalityLog(Base, TimestampMixin):
    """Daily mortality tracking per species/batch."""
    __tablename__ = "mortality_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    batch_or_flock_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    cause: Mapped[Optional[str]] = mapped_column(String(100))  # disease | predator | accident | unknown
    disease_alert_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("disease_alerts.id"))
    disposed_by: Mapped[Optional[str]] = mapped_column(String(50))  # burial | incineration | composting
    recorded_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
