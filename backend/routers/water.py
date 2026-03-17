"""Water system — sources, tanks, irrigation zones, usage logs, quality tests."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.water import (
    WaterSource, WaterStorageTank, IrrigationZone,
    IrrigationLog, WaterUsageLog, WaterQualityTest,
)
from backend.schemas import (
    WaterSourceCreate, WaterSourceOut,
    WaterStorageTankCreate, WaterStorageTankOut,
    IrrigationZoneCreate, IrrigationZoneOut,
    IrrigationLogCreate, IrrigationLogOut,
    WaterUsageLogCreate, WaterUsageLogOut,
    WaterQualityTestCreate, WaterQualityTestOut,
)

router = APIRouter(prefix="/api/water", tags=["Water System"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


def _require_write(current_user: User):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient permissions")


# ── Water Sources ─────────────────────────────────────────────────────────────

@router.post("/sources", response_model=WaterSourceOut)
def create_source(
    data: WaterSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    source = WaterSource(**data.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/sources", response_model=list[WaterSourceOut])
def list_sources(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterSource)
    if active_only:
        q = q.filter(WaterSource.is_active == True)
    return q.order_by(WaterSource.name).all()


@router.put("/sources/{source_id}/deactivate")
def deactivate_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    src = db.query(WaterSource).filter(WaterSource.id == source_id).first()
    if not src:
        raise HTTPException(404, "Water source not found")
    src.is_active = False
    db.commit()
    return {"id": source_id, "is_active": False}


# ── Storage Tanks ─────────────────────────────────────────────────────────────

@router.post("/tanks", response_model=WaterStorageTankOut)
def create_tank(
    data: WaterStorageTankCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    tank = WaterStorageTank(**data.model_dump())
    db.add(tank)
    db.commit()
    db.refresh(tank)
    return tank


@router.get("/tanks", response_model=list[WaterStorageTankOut])
def list_tanks(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterStorageTank)
    if active_only:
        q = q.filter(WaterStorageTank.is_active == True)
    return q.order_by(WaterStorageTank.name).all()


@router.patch("/tanks/{tank_id}/level")
def update_tank_level(
    tank_id: int,
    current_level_liters: float = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tank = db.query(WaterStorageTank).filter(WaterStorageTank.id == tank_id).first()
    if not tank:
        raise HTTPException(404, "Tank not found")
    if current_level_liters < 0 or current_level_liters > tank.capacity_liters:
        raise HTTPException(400, "Level out of range for tank capacity")
    tank.current_level_liters = current_level_liters
    db.commit()
    return {"id": tank_id, "current_level_liters": current_level_liters,
            "fill_pct": round(current_level_liters / tank.capacity_liters * 100, 1)}


# ── Irrigation Zones ──────────────────────────────────────────────────────────

@router.post("/zones", response_model=IrrigationZoneOut)
def create_zone(
    data: IrrigationZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    zone = IrrigationZone(**data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.get("/zones", response_model=list[IrrigationZoneOut])
def list_zones(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(IrrigationZone)
    if active_only:
        q = q.filter(IrrigationZone.is_active == True)
    return q.order_by(IrrigationZone.name).all()


# ── Irrigation Logs ───────────────────────────────────────────────────────────

@router.post("/irrigation-logs", response_model=IrrigationLogOut)
def create_irrigation_log(
    data: IrrigationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    zone = db.query(IrrigationZone).filter(IrrigationZone.id == data.zone_id).first()
    if not zone:
        raise HTTPException(404, "Irrigation zone not found")
    log = IrrigationLog(**data.model_dump(), recorded_by=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/irrigation-logs", response_model=list[IrrigationLogOut])
def list_irrigation_logs(
    zone_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(IrrigationLog)
    if zone_id:
        q = q.filter(IrrigationLog.zone_id == zone_id)
    if date_from:
        q = q.filter(IrrigationLog.irrigation_date >= date_from)
    if date_to:
        q = q.filter(IrrigationLog.irrigation_date <= date_to)
    return q.order_by(IrrigationLog.irrigation_date.desc()).all()


@router.get("/irrigation-logs/summary")
def irrigation_summary(
    zone_id: Optional[int] = None,
    days: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=days)
    q = db.query(
        IrrigationLog.zone_id,
        func.count(IrrigationLog.id).label("events"),
        func.sum(IrrigationLog.volume_liters).label("total_liters"),
        func.sum(IrrigationLog.duration_minutes).label("total_minutes"),
    ).filter(IrrigationLog.irrigation_date >= cutoff)
    if zone_id:
        q = q.filter(IrrigationLog.zone_id == zone_id)
    rows = q.group_by(IrrigationLog.zone_id).all()
    return [
        {
            "zone_id": r.zone_id,
            "events": r.events,
            "total_liters": r.total_liters or 0,
            "total_minutes": r.total_minutes or 0,
        }
        for r in rows
    ]


# ── Water Usage Logs ──────────────────────────────────────────────────────────

@router.post("/usage-logs", response_model=WaterUsageLogOut)
def create_usage_log(
    data: WaterUsageLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    src = db.query(WaterSource).filter(WaterSource.id == data.source_id).first()
    if not src:
        raise HTTPException(404, "Water source not found")
    log = WaterUsageLog(**data.model_dump(), recorded_by=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/usage-logs", response_model=list[WaterUsageLogOut])
def list_usage_logs(
    source_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    purpose: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterUsageLog)
    if source_id:
        q = q.filter(WaterUsageLog.source_id == source_id)
    if date_from:
        q = q.filter(WaterUsageLog.log_date >= date_from)
    if date_to:
        q = q.filter(WaterUsageLog.log_date <= date_to)
    if purpose:
        q = q.filter(WaterUsageLog.purpose == purpose)
    return q.order_by(WaterUsageLog.log_date.desc()).all()


@router.get("/usage-logs/summary")
def usage_summary(
    days: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=days)
    rows = db.query(
        WaterUsageLog.source_id,
        WaterUsageLog.purpose,
        func.sum(WaterUsageLog.volume_liters).label("total_liters"),
        func.sum(WaterUsageLog.energy_kwh).label("total_kwh"),
    ).filter(
        WaterUsageLog.log_date >= cutoff
    ).group_by(WaterUsageLog.source_id, WaterUsageLog.purpose).all()
    return [
        {
            "source_id": r.source_id,
            "purpose": r.purpose,
            "total_liters": r.total_liters or 0,
            "total_kwh": r.total_kwh or 0,
        }
        for r in rows
    ]


# ── Water Quality Tests ───────────────────────────────────────────────────────

@router.post("/quality-tests", response_model=WaterQualityTestOut)
def create_quality_test(
    data: WaterQualityTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    src = db.query(WaterSource).filter(WaterSource.id == data.source_id).first()
    if not src:
        raise HTTPException(404, "Water source not found")
    test = WaterQualityTest(**data.model_dump(), tested_by=current_user.id)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.get("/quality-tests", response_model=list[WaterQualityTestOut])
def list_quality_tests(
    source_id: Optional[int] = None,
    date_from: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterQualityTest)
    if source_id:
        q = q.filter(WaterQualityTest.source_id == source_id)
    if date_from:
        q = q.filter(WaterQualityTest.test_date >= date_from)
    return q.order_by(WaterQualityTest.test_date.desc()).all()


@router.get("/quality-tests/{source_id}/latest", response_model=WaterQualityTestOut)
def get_latest_quality_test(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = (
        db.query(WaterQualityTest)
        .filter(WaterQualityTest.source_id == source_id)
        .order_by(WaterQualityTest.test_date.desc())
        .first()
    )
    if not test:
        raise HTTPException(404, "No quality tests found for this source")
    return test
