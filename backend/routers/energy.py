"""Solar & energy — arrays, inverters, generation, consumption, battery, grid events."""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.energy import (
    SolarArray, Inverter, EnergyGenerationLog,
    EnergyConsumptionLog, BatteryBank, GridEvent,
)
from backend.schemas import (
    SolarArrayCreate, SolarArrayOut,
    InverterCreate, InverterOut,
    EnergyGenerationLogCreate, EnergyGenerationLogOut,
    EnergyConsumptionLogCreate, EnergyConsumptionLogOut,
    BatteryBankCreate, BatteryBankOut,
    GridEventCreate, GridEventOut,
)

router = APIRouter(prefix="/api/energy", tags=["Solar & Energy"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


def _require_write(current_user: User):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient permissions")


# ── Solar Arrays ──────────────────────────────────────────────────────────────

@router.post("/arrays", response_model=SolarArrayOut)
def create_array(
    data: SolarArrayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    arr = SolarArray(**data.model_dump())
    db.add(arr)
    db.commit()
    db.refresh(arr)
    return arr


@router.get("/arrays", response_model=list[SolarArrayOut])
def list_arrays(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SolarArray)
    if active_only:
        q = q.filter(SolarArray.is_active == True)
    return q.order_by(SolarArray.name).all()


@router.put("/arrays/{array_id}/deactivate")
def deactivate_array(
    array_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    arr = db.query(SolarArray).filter(SolarArray.id == array_id).first()
    if not arr:
        raise HTTPException(404, "Solar array not found")
    arr.is_active = False
    db.commit()
    return {"id": array_id, "is_active": False}


# ── Inverters ─────────────────────────────────────────────────────────────────

@router.post("/inverters", response_model=InverterOut)
def create_inverter(
    data: InverterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    inv = Inverter(**data.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.get("/inverters", response_model=list[InverterOut])
def list_inverters(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Inverter)
    if active_only:
        q = q.filter(Inverter.is_active == True)
    return q.order_by(Inverter.name).all()


# ── Generation Logs ───────────────────────────────────────────────────────────

@router.post("/generation", response_model=EnergyGenerationLogOut)
def create_generation_log(
    data: EnergyGenerationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    arr = db.query(SolarArray).filter(SolarArray.id == data.solar_array_id).first()
    if not arr:
        raise HTTPException(404, "Solar array not found")
    log = EnergyGenerationLog(**data.model_dump(), recorded_by=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/generation", response_model=list[EnergyGenerationLogOut])
def list_generation_logs(
    solar_array_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(EnergyGenerationLog)
    if solar_array_id:
        q = q.filter(EnergyGenerationLog.solar_array_id == solar_array_id)
    if date_from:
        q = q.filter(EnergyGenerationLog.log_date >= date_from)
    if date_to:
        q = q.filter(EnergyGenerationLog.log_date <= date_to)
    return q.order_by(EnergyGenerationLog.log_date.desc()).all()


@router.get("/generation/summary")
def generation_summary(
    days: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cutoff = date.today() - timedelta(days=days)
    rows = db.query(
        EnergyGenerationLog.solar_array_id,
        func.sum(EnergyGenerationLog.units_generated_kwh).label("total_kwh"),
        func.avg(EnergyGenerationLog.sunshine_hours).label("avg_sunshine"),
        func.count(EnergyGenerationLog.id).label("days_logged"),
    ).filter(
        EnergyGenerationLog.log_date >= cutoff
    ).group_by(EnergyGenerationLog.solar_array_id).all()
    return [
        {
            "solar_array_id": r.solar_array_id,
            "total_kwh": round(r.total_kwh or 0, 2),
            "avg_sunshine_hours": round(r.avg_sunshine or 0, 1),
            "days_logged": r.days_logged,
        }
        for r in rows
    ]


# ── Consumption Logs ──────────────────────────────────────────────────────────

@router.post("/consumption", response_model=EnergyConsumptionLogOut)
def create_consumption_log(
    data: EnergyConsumptionLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    log = EnergyConsumptionLog(**data.model_dump(), recorded_by=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/consumption", response_model=list[EnergyConsumptionLogOut])
def list_consumption_logs(
    section: Optional[str] = None,
    source: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(EnergyConsumptionLog)
    if section:
        q = q.filter(EnergyConsumptionLog.section == section)
    if source:
        q = q.filter(EnergyConsumptionLog.source == source)
    if date_from:
        q = q.filter(EnergyConsumptionLog.log_date >= date_from)
    if date_to:
        q = q.filter(EnergyConsumptionLog.log_date <= date_to)
    return q.order_by(EnergyConsumptionLog.log_date.desc()).all()


@router.get("/consumption/summary")
def consumption_summary(
    days: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cutoff = date.today() - timedelta(days=days)
    rows = db.query(
        EnergyConsumptionLog.section,
        EnergyConsumptionLog.source,
        func.sum(EnergyConsumptionLog.units_consumed_kwh).label("total_kwh"),
        func.sum(EnergyConsumptionLog.cost).label("total_cost"),
    ).filter(
        EnergyConsumptionLog.log_date >= cutoff
    ).group_by(
        EnergyConsumptionLog.section, EnergyConsumptionLog.source
    ).all()
    return [
        {
            "section": r.section,
            "source": r.source,
            "total_kwh": round(r.total_kwh or 0, 2),
            "total_cost": round(r.total_cost or 0, 2),
        }
        for r in rows
    ]


@router.get("/dashboard")
def energy_dashboard(
    days: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Net energy balance: generated vs consumed over last N days."""
    cutoff = date.today() - timedelta(days=days)
    gen = db.query(func.sum(EnergyGenerationLog.units_generated_kwh)).filter(
        EnergyGenerationLog.log_date >= cutoff
    ).scalar() or 0
    con = db.query(func.sum(EnergyConsumptionLog.units_consumed_kwh)).filter(
        EnergyConsumptionLog.log_date >= cutoff
    ).scalar() or 0
    grid_outages = db.query(func.count(GridEvent.id)).filter(
        GridEvent.event_date >= cutoff,
        GridEvent.event_type == "outage",
    ).scalar() or 0
    return {
        "period_days": days,
        "total_generated_kwh": round(gen, 2),
        "total_consumed_kwh": round(con, 2),
        "net_surplus_kwh": round(gen - con, 2),
        "self_sufficiency_pct": round(gen / con * 100, 1) if con > 0 else 100.0,
        "grid_outages": grid_outages,
    }


# ── Battery Banks ─────────────────────────────────────────────────────────────

@router.post("/batteries", response_model=BatteryBankOut)
def create_battery_bank(
    data: BatteryBankCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    bank = BatteryBank(**data.model_dump())
    db.add(bank)
    db.commit()
    db.refresh(bank)
    return bank


@router.get("/batteries", response_model=list[BatteryBankOut])
def list_battery_banks(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(BatteryBank)
    if active_only:
        q = q.filter(BatteryBank.is_active == True)
    return q.all()


@router.patch("/batteries/{bank_id}/soc")
def update_battery_soc(
    bank_id: int,
    soc_pct: float = Query(..., ge=0, le=100),
    cycles_completed: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bank = db.query(BatteryBank).filter(BatteryBank.id == bank_id).first()
    if not bank:
        raise HTTPException(404, "Battery bank not found")
    bank.current_soc_pct = soc_pct
    if cycles_completed is not None:
        bank.cycles_completed = cycles_completed
    db.commit()
    return {"id": bank_id, "current_soc_pct": soc_pct}


# ── Grid Events ───────────────────────────────────────────────────────────────

@router.post("/grid-events", response_model=GridEventOut)
def create_grid_event(
    data: GridEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    event = GridEvent(**data.model_dump(), reported_by=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/grid-events", response_model=list[GridEventOut])
def list_grid_events(
    event_type: Optional[str] = None,
    date_from: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(GridEvent)
    if event_type:
        q = q.filter(GridEvent.event_type == event_type)
    if date_from:
        q = q.filter(GridEvent.event_date >= date_from)
    return q.order_by(GridEvent.event_date.desc()).all()
