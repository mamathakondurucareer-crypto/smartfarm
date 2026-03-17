"""Sensor Calibration Tracker — calibration logs, battery replacements, firmware updates."""

from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.sensor import SensorDevice, SensorCalibrationLog, BatteryReplacementLog, CameraFirmwareLog
from backend.schemas import (
    SensorCalibrationLogCreate, SensorCalibrationLogOut,
    BatteryReplacementLogCreate, BatteryReplacementLogOut,
    CameraFirmwareLogCreate, CameraFirmwareLogOut,
)

router = APIRouter(prefix="/api/sensor-calibration", tags=["Sensor Calibration"])

_WRITE_ROLES = ("admin", "manager", "supervisor", "technician")
_CALIBRATION_INTERVAL_DAYS = 90


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Calibration Logs ──────────────────────────────────────────────────────────

@router.post("/calibrations", response_model=SensorCalibrationLogOut)
def log_calibration(
    data: SensorCalibrationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    sensor = db.query(SensorDevice).filter(SensorDevice.id == data.sensor_id).first()
    if not sensor:
        raise HTTPException(404, "Sensor not found")

    cal = SensorCalibrationLog(**data.model_dump())
    db.add(cal)

    # Update sensor's calibration_date
    sensor.calibration_date = data.calibration_date

    db.commit()
    db.refresh(cal)
    return cal


@router.get("/calibrations", response_model=list[SensorCalibrationLogOut])
def list_calibrations(
    sensor_id: Optional[int] = None,
    passed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SensorCalibrationLog)
    if sensor_id:
        q = q.filter(SensorCalibrationLog.sensor_id == sensor_id)
    if passed is not None:
        q = q.filter(SensorCalibrationLog.passed == passed)
    return q.order_by(SensorCalibrationLog.calibration_date.desc()).all()


@router.get("/calibrations/due")
def sensors_due_for_calibration(
    days_threshold: int = Query(default=_CALIBRATION_INTERVAL_DAYS),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return sensors whose last calibration is older than the threshold (default 90 days)."""
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days_threshold)
    sensors = db.query(SensorDevice).all()

    due = []
    for s in sensors:
        last_cal = s.calibration_date
        if last_cal is None or last_cal < cutoff:
            days_since = None
            if last_cal:
                # Ensure timezone-aware comparison
                if last_cal.tzinfo is None:
                    from datetime import timezone as tz
                    last_cal = last_cal.replace(tzinfo=timezone.utc)
                days_since = (datetime.now(tz=timezone.utc) - last_cal).days
            due.append({
                "sensor_id": s.id,
                "device_id": s.device_id,
                "name": s.name,
                "zone": s.zone,
                "sensor_type": s.sensor_type,
                "last_calibration": last_cal.isoformat() if last_cal else None,
                "days_since_calibration": days_since,
                "status": s.status,
            })

    return {
        "threshold_days": days_threshold,
        "sensors_due_count": len(due),
        "sensors": sorted(due, key=lambda x: (x["days_since_calibration"] or 9999), reverse=True),
    }


# ── Battery Replacement Logs ──────────────────────────────────────────────────

@router.post("/battery-replacements", response_model=BatteryReplacementLogOut)
def log_battery_replacement(
    data: BatteryReplacementLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    sensor = db.query(SensorDevice).filter(SensorDevice.id == data.sensor_id).first()
    if not sensor:
        raise HTTPException(404, "Sensor not found")
    log = BatteryReplacementLog(**data.model_dump())
    db.add(log)

    # Update sensor battery tracking
    if hasattr(sensor, "battery_level"):
        sensor.battery_level = 100.0

    db.commit()
    db.refresh(log)
    return log


@router.get("/battery-replacements", response_model=list[BatteryReplacementLogOut])
def list_battery_replacements(
    sensor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(BatteryReplacementLog)
    if sensor_id:
        q = q.filter(BatteryReplacementLog.sensor_id == sensor_id)
    return q.order_by(BatteryReplacementLog.replacement_date.desc()).all()


@router.get("/battery-replacements/schedule")
def battery_replacement_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return sensors with low battery or upcoming replacement due dates."""
    sensors = db.query(SensorDevice).all()
    schedule = []
    for s in sensors:
        # Get latest replacement
        latest = (
            db.query(BatteryReplacementLog)
            .filter(BatteryReplacementLog.sensor_id == s.id)
            .order_by(BatteryReplacementLog.replacement_date.desc())
            .first()
        )
        next_due = latest.next_replacement_due if latest else None
        low_battery = s.battery_level is not None and s.battery_level < 20

        if low_battery or next_due:
            schedule.append({
                "sensor_id": s.id,
                "device_id": s.device_id,
                "name": s.name,
                "zone": s.zone,
                "battery_level": s.battery_level,
                "low_battery": low_battery,
                "next_replacement_due": next_due.isoformat() if next_due else None,
                "last_replaced": latest.replacement_date.isoformat() if latest else None,
            })

    return {"sensors_count": len(schedule), "sensors": schedule}


# ── Firmware Update Logs ──────────────────────────────────────────────────────

@router.post("/firmware-updates", response_model=CameraFirmwareLogOut)
def log_firmware_update(
    data: CameraFirmwareLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    sensor = db.query(SensorDevice).filter(SensorDevice.id == data.sensor_id).first()
    if not sensor:
        raise HTTPException(404, "Sensor not found")
    log = CameraFirmwareLog(**data.model_dump())
    db.add(log)
    sensor.firmware_version = data.new_version
    db.commit()
    db.refresh(log)
    return log


@router.get("/firmware-updates", response_model=list[CameraFirmwareLogOut])
def list_firmware_updates(
    sensor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(CameraFirmwareLog)
    if sensor_id:
        q = q.filter(CameraFirmwareLog.sensor_id == sensor_id)
    return q.order_by(CameraFirmwareLog.update_date.desc()).all()


@router.get("/summary")
def calibration_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Overview of sensor calibration health across the farm."""
    total_sensors = db.query(SensorDevice).count()
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=_CALIBRATION_INTERVAL_DAYS)
    sensors = db.query(SensorDevice).all()

    overdue = 0
    never_calibrated = 0
    for s in sensors:
        if s.calibration_date is None:
            never_calibrated += 1
        else:
            cal = s.calibration_date
            if cal.tzinfo is None:
                cal = cal.replace(tzinfo=timezone.utc)
            if cal < cutoff:
                overdue += 1

    recent_cals = db.query(SensorCalibrationLog).order_by(
        SensorCalibrationLog.calibration_date.desc()
    ).limit(5).all()

    return {
        "total_sensors": total_sensors,
        "overdue_calibration": overdue,
        "never_calibrated": never_calibrated,
        "calibration_interval_days": _CALIBRATION_INTERVAL_DAYS,
        "recent_calibrations": [
            {
                "id": c.id,
                "sensor_id": c.sensor_id,
                "calibration_date": c.calibration_date.isoformat(),
                "technician": c.technician,
                "passed": c.passed,
            }
            for c in recent_cals
        ],
    }
