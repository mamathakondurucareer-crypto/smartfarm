"""Vaccination schedules, disease alerts, treatment logs, and mortality tracking."""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.vaccination import (
    VaccinationSchedule, VaccinationRecord,
    DiseaseAlert, TreatmentLog, MortalityLog,
)
from backend.schemas import (
    VaccinationScheduleCreate, VaccinationScheduleOut,
    VaccinationRecordCreate, VaccinationRecordOut,
    DiseaseAlertCreate, DiseaseAlertOut, DiseaseAlertUpdate,
    TreatmentLogCreate, TreatmentLogOut,
    MortalityLogCreate, MortalityLogOut,
)

router = APIRouter(prefix="/api/vaccination", tags=["Vaccination & Disease"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


def _require_write(current_user: User):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient permissions")


# ── Vaccination Schedules ────────────────────────────────────────────────────

@router.post("/schedules", response_model=VaccinationScheduleOut)
def create_schedule(
    data: VaccinationScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    schedule = VaccinationSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=list[VaccinationScheduleOut])
def list_schedules(
    species: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(VaccinationSchedule)
    if species:
        q = q.filter(VaccinationSchedule.species == species)
    return q.order_by(VaccinationSchedule.species, VaccinationSchedule.vaccine_name).all()


# ── Vaccination Records ──────────────────────────────────────────────────────

@router.post("/records", response_model=VaccinationRecordOut)
def create_vaccination_record(
    data: VaccinationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    schedule = db.query(VaccinationSchedule).filter(
        VaccinationSchedule.id == data.schedule_id
    ).first()
    if not schedule:
        raise HTTPException(404, "Vaccination schedule not found")

    # Auto-compute next due date
    next_due = None
    if schedule.repeat_interval_days and schedule.repeat_interval_days > 0:
        next_due = data.vaccination_date + timedelta(days=schedule.repeat_interval_days)

    record = VaccinationRecord(
        **data.model_dump(),
        vaccinated_by=current_user.id,
        next_due_date=next_due,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/records", response_model=list[VaccinationRecordOut])
def list_vaccination_records(
    species: Optional[str] = None,
    schedule_id: Optional[int] = None,
    batch_or_flock_ref: Optional[str] = None,
    due_before: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(VaccinationRecord)
    if species:
        q = q.filter(VaccinationRecord.species == species)
    if schedule_id:
        q = q.filter(VaccinationRecord.schedule_id == schedule_id)
    if batch_or_flock_ref:
        q = q.filter(VaccinationRecord.batch_or_flock_ref == batch_or_flock_ref)
    if due_before:
        q = q.filter(VaccinationRecord.next_due_date <= due_before)
    return q.order_by(VaccinationRecord.vaccination_date.desc()).all()


@router.get("/records/due-soon", response_model=list[VaccinationRecordOut])
def get_due_soon(
    days_ahead: int = Query(default=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Records with next_due_date within the next N days."""
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    return (
        db.query(VaccinationRecord)
        .filter(
            VaccinationRecord.next_due_date >= today,
            VaccinationRecord.next_due_date <= cutoff,
        )
        .order_by(VaccinationRecord.next_due_date)
        .all()
    )


# ── Disease Alerts ───────────────────────────────────────────────────────────

@router.post("/disease-alerts", response_model=DiseaseAlertOut)
def create_disease_alert(
    data: DiseaseAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = DiseaseAlert(
        **data.model_dump(),
        status="suspected",
        reported_by=current_user.id,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/disease-alerts", response_model=list[DiseaseAlertOut])
def list_disease_alerts(
    species: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    date_from: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(DiseaseAlert)
    if species:
        q = q.filter(DiseaseAlert.species == species)
    if status:
        q = q.filter(DiseaseAlert.status == status)
    if severity:
        q = q.filter(DiseaseAlert.severity == severity)
    if date_from:
        q = q.filter(DiseaseAlert.alert_date >= date_from)
    return q.order_by(DiseaseAlert.alert_date.desc()).all()


@router.get("/disease-alerts/{alert_id}", response_model=DiseaseAlertOut)
def get_disease_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(DiseaseAlert).filter(DiseaseAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Disease alert not found")
    return alert


@router.patch("/disease-alerts/{alert_id}", response_model=DiseaseAlertOut)
def update_disease_alert(
    alert_id: int,
    data: DiseaseAlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    alert = db.query(DiseaseAlert).filter(DiseaseAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Disease alert not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(alert, k, v)
    db.commit()
    db.refresh(alert)
    return alert


# ── Treatment Logs ───────────────────────────────────────────────────────────

@router.post("/treatments", response_model=TreatmentLogOut)
def create_treatment_log(
    data: TreatmentLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    alert = db.query(DiseaseAlert).filter(DiseaseAlert.id == data.disease_alert_id).first()
    if not alert:
        raise HTTPException(404, "Disease alert not found")

    withdrawal_end = None
    if data.withdrawal_period_days > 0:
        withdrawal_end = data.treatment_date + timedelta(
            days=data.duration_days + data.withdrawal_period_days
        )

    treatment = TreatmentLog(
        **data.model_dump(),
        withdrawal_end_date=withdrawal_end,
        administered_by=current_user.id,
    )
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment


@router.get("/treatments/{alert_id}", response_model=list[TreatmentLogOut])
def get_treatments_for_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(TreatmentLog)
        .filter(TreatmentLog.disease_alert_id == alert_id)
        .order_by(TreatmentLog.treatment_date)
        .all()
    )


@router.patch("/treatments/{treatment_id}/outcome")
def update_treatment_outcome(
    treatment_id: int,
    outcome: str = Query(..., description="improving | stable | worsening | recovered"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    treatment = db.query(TreatmentLog).filter(TreatmentLog.id == treatment_id).first()
    if not treatment:
        raise HTTPException(404, "Treatment record not found")
    treatment.outcome = outcome
    db.commit()
    return {"id": treatment_id, "outcome": outcome}


# ── Mortality Logs ───────────────────────────────────────────────────────────

@router.post("/mortality", response_model=MortalityLogOut)
def create_mortality_log(
    data: MortalityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = MortalityLog(**data.model_dump(), recorded_by=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/mortality", response_model=list[MortalityLogOut])
def list_mortality_logs(
    species: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(MortalityLog)
    if species:
        q = q.filter(MortalityLog.species == species)
    if date_from:
        q = q.filter(MortalityLog.log_date >= date_from)
    if date_to:
        q = q.filter(MortalityLog.log_date <= date_to)
    return q.order_by(MortalityLog.log_date.desc()).all()


@router.get("/mortality/summary")
def mortality_summary(
    species: Optional[str] = None,
    days: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func
    cutoff = date.today() - __import__("datetime").timedelta(days=days)
    q = db.query(
        MortalityLog.species,
        MortalityLog.cause,
        func.sum(MortalityLog.count).label("total"),
    ).filter(MortalityLog.log_date >= cutoff)
    if species:
        q = q.filter(MortalityLog.species == species)
    rows = q.group_by(MortalityLog.species, MortalityLog.cause).all()
    return [{"species": r.species, "cause": r.cause, "total": r.total} for r in rows]
