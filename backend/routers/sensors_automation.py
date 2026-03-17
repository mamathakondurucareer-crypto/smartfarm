"""Sensor data ingestion and automation endpoints."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.sensor import SensorDevice, SensorReading, Alert
from backend.models.automation import AutomationRule, AutomationLog
from backend.models.drone import DroneFlightLog
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import SensorReadingCreate, SensorReadingBulk, SensorDeviceOut, AlertOut
from backend.services.alert_service import check_threshold

_MGMT_ROLES = ("admin", "manager", "supervisor")

sensors_router = APIRouter(prefix="/api/sensors", tags=["Sensors & IoT"])
automation_router = APIRouter(prefix="/api/automation", tags=["Automation"])


# ═══════ SENSORS ═══════
@sensors_router.get("/devices", response_model=list[SensorDeviceOut])
def list_devices(zone: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(SensorDevice)
    if zone:
        q = q.filter(SensorDevice.zone == zone)
    if status:
        q = q.filter(SensorDevice.status == status)
    return q.order_by(SensorDevice.zone, SensorDevice.name).all()


@sensors_router.post("/readings", status_code=201)
def ingest_reading(data: SensorReadingCreate, db: Session = Depends(get_db)):
    reading = SensorReading(
        device_id=data.device_id, recorded_at=data.recorded_at,
        parameter=data.parameter, value=data.value, unit=data.unit,
    )
    db.add(reading)
    device = db.query(SensorDevice).filter(SensorDevice.id == data.device_id).first()
    if device:
        device.last_reading_at = data.recorded_at
    alert = check_threshold(db, data.parameter, data.value, device.zone if device else "unknown", data.device_id)
    db.commit()
    result = {"id": reading.id}
    if alert:
        result["alert"] = {"type": alert.alert_type, "message": alert.message}
    return result


@sensors_router.post("/readings/bulk", status_code=201)
def ingest_bulk(data: SensorReadingBulk, db: Session = Depends(get_db)):
    alerts = []
    for r in data.readings:
        reading = SensorReading(device_id=r.device_id, recorded_at=r.recorded_at, parameter=r.parameter, value=r.value, unit=r.unit)
        db.add(reading)
        device = db.query(SensorDevice).filter(SensorDevice.id == r.device_id).first()
        if device:
            device.last_reading_at = r.recorded_at
        a = check_threshold(db, r.parameter, r.value, device.zone if device else "unknown", r.device_id)
        if a:
            alerts.append(a.message)
    db.commit()
    return {"ingested": len(data.readings), "alerts": alerts}


@sensors_router.get("/readings/{device_id}")
def get_readings(
    device_id: int,
    parameter: Optional[str] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    q = db.query(SensorReading).filter(SensorReading.device_id == device_id)
    if parameter:
        q = q.filter(SensorReading.parameter == parameter)
    return q.order_by(SensorReading.recorded_at.desc()).limit(limit).all()


@sensors_router.get("/latest-by-zone/{zone}")
def latest_by_zone(zone: str, db: Session = Depends(get_db)):
    devices = db.query(SensorDevice).filter(SensorDevice.zone == zone).all()
    result = {}
    for d in devices:
        latest = db.query(SensorReading).filter(SensorReading.device_id == d.id).order_by(SensorReading.recorded_at.desc()).first()
        if latest:
            result[f"{d.name}_{latest.parameter}"] = {"value": latest.value, "unit": latest.unit, "at": str(latest.recorded_at)}
    return result


# ═══════ SUMMARY ENDPOINTS ═══════
@sensors_router.get("/latest-all")
def latest_all(db: Session = Depends(get_db)):
    """Return the latest reading for each parameter per zone."""
    subq = (
        db.query(
            SensorReading.device_id,
            SensorReading.parameter,
            func.max(SensorReading.recorded_at).label("max_at"),
        )
        .group_by(SensorReading.device_id, SensorReading.parameter)
        .subquery()
    )
    rows = (
        db.query(SensorReading, SensorDevice.zone)
        .join(
            subq,
            (SensorReading.device_id == subq.c.device_id)
            & (SensorReading.parameter == subq.c.parameter)
            & (SensorReading.recorded_at == subq.c.max_at),
        )
        .join(SensorDevice, SensorDevice.id == SensorReading.device_id)
        .all()
    )
    result: dict = {}
    for reading, zone in rows:
        zone_data = result.setdefault(zone, {})
        zone_data[reading.parameter] = {
            "value": reading.value,
            "unit": reading.unit,
            "at": reading.recorded_at.isoformat(),
        }
    return result


@sensors_router.get("/water-summary")
def water_summary(db: Session = Depends(get_db)):
    """Return latest reservoir and header-tank levels."""
    device = db.query(SensorDevice).filter(SensorDevice.device_id == "SFDEV-RESERVOIR").first()
    result = {"reservoirLevel": None, "headerTankLevel": None}
    if device:
        for param, key in [("water_level", "reservoirLevel"), ("header_tank_level", "headerTankLevel")]:
            latest = (
                db.query(SensorReading)
                .filter(SensorReading.device_id == device.id, SensorReading.parameter == param)
                .order_by(SensorReading.recorded_at.desc())
                .first()
            )
            if latest:
                result[key] = latest.value
    return result


@sensors_router.get("/energy-summary")
def energy_summary(db: Session = Depends(get_db)):
    """Return latest solar generation, consumption and grid export."""
    device = db.query(SensorDevice).filter(SensorDevice.device_id == "SFDEV-ENERGY").first()
    result = {"solarGeneration": None, "farmConsumption": None, "gridExport": None}
    if device:
        for param, key in [
            ("solar_generation", "solarGeneration"),
            ("consumption", "farmConsumption"),
            ("grid_export", "gridExport"),
        ]:
            latest = (
                db.query(SensorReading)
                .filter(SensorReading.device_id == device.id, SensorReading.parameter == param)
                .order_by(SensorReading.recorded_at.desc())
                .first()
            )
            if latest:
                result[key] = latest.value
    return result


# ═══════ ALERTS ═══════
@sensors_router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    resolved: Optional[bool] = None,
    alert_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if resolved is not None:
        q = q.filter(Alert.resolved == resolved)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    return q.order_by(Alert.created_at.desc()).limit(limit).all()


@sensors_router.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = True
    alert.acknowledged_by = current_user.username
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Alert acknowledged"}


@sensors_router.put("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, notes: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolution_notes = notes
    db.commit()
    return {"message": "Alert resolved"}


# ═══════ AUTOMATION ═══════
@automation_router.get("/rules")
def list_rules(system: Optional[str] = None, enabled: Optional[bool] = None, db: Session = Depends(get_db)):
    q = db.query(AutomationRule).filter(AutomationRule.is_active == True)
    if system:
        q = q.filter(AutomationRule.system == system)
    if enabled is not None:
        q = q.filter(AutomationRule.enabled == enabled)
    return q.order_by(AutomationRule.priority).all()


@automation_router.put("/rules/{rule_id}/toggle")
def toggle_rule(rule_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in _MGMT_ROLES:
        raise HTTPException(403, "Manager or supervisor role required to toggle automation rules")
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "Rule not found")
    rule.enabled = not rule.enabled
    db.commit()
    return {"rule": rule.name, "enabled": rule.enabled}


@automation_router.get("/logs")
def list_auto_logs(rule_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(AutomationLog)
    if rule_id:
        q = q.filter(AutomationLog.rule_id == rule_id)
    return q.order_by(AutomationLog.executed_at.desc()).limit(limit).all()


@automation_router.get("/status")
def automation_status(db: Session = Depends(get_db)):
    """Return automation system status summary grouped by system."""
    rules = db.query(AutomationRule).filter(AutomationRule.is_active == True).all()
    status: dict = {}
    for rule in rules:
        entry = status.setdefault(rule.system, {"enabled": 0, "disabled": 0, "total": 0, "rules": []})
        entry["total"] += 1
        if rule.enabled:
            entry["enabled"] += 1
        else:
            entry["disabled"] += 1
        entry["rules"].append({"id": rule.id, "name": rule.name, "enabled": rule.enabled})
    return status


@automation_router.get("/drone-flights")
def list_flights(drone_id: Optional[str] = None, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(DroneFlightLog)
    if drone_id:
        q = q.filter(DroneFlightLog.drone_id == drone_id)
    return q.order_by(DroneFlightLog.flight_date.desc()).limit(limit).all()
