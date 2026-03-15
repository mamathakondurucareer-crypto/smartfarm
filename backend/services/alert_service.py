"""Alert service: sensor threshold monitoring and alert generation."""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.models.sensor import Alert
from backend.config import get_settings

settings = get_settings()

THRESHOLDS = {
    "dissolved_oxygen": {"critical_low": 4.0, "warning_low": 4.5, "unit": "mg/L", "system": "aquaculture"},
    "ammonia": {"critical_high": 0.05, "warning_high": 0.03, "unit": "mg/L", "system": "aquaculture"},
    "ph": {"warning_low": 6.5, "warning_high": 8.5, "unit": "", "system": "aquaculture"},
    "water_temp": {"warning_high": 32, "critical_high": 35, "unit": "°C", "system": "aquaculture"},
    "gh_temp": {"warning_high": 36, "critical_high": 38, "unit": "°C", "system": "greenhouse"},
    "gh_humidity": {"warning_high": 85, "critical_high": 90, "unit": "%", "system": "greenhouse"},
    "poultry_ammonia": {"warning_high": 15, "critical_high": 20, "unit": "ppm", "system": "poultry"},
    "reservoir_level": {"warning_low": 30, "critical_low": 20, "unit": "%", "system": "water"},
    "soil_moisture": {"warning_low": 25, "critical_low": 18, "unit": "%", "system": "irrigation"},
}


def check_threshold(db: Session, parameter: str, value: float, zone: str, device_id: int = None) -> Alert | None:
    thresholds = THRESHOLDS.get(parameter)
    if not thresholds:
        return None

    alert_type = None
    message = None

    crit_low = thresholds.get("critical_low")
    warn_low = thresholds.get("warning_low")
    crit_high = thresholds.get("critical_high")
    warn_high = thresholds.get("warning_high")
    unit = thresholds.get("unit", "")
    system = thresholds.get("system", "general")

    if crit_low is not None and value <= crit_low:
        alert_type = "critical"
        message = f"CRITICAL: {parameter} at {value}{unit} (threshold: {crit_low}{unit}) in {zone}"
    elif warn_low is not None and value <= warn_low:
        alert_type = "warning"
        message = f"WARNING: {parameter} low at {value}{unit} (threshold: {warn_low}{unit}) in {zone}"
    elif crit_high is not None and value >= crit_high:
        alert_type = "critical"
        message = f"CRITICAL: {parameter} at {value}{unit} (threshold: {crit_high}{unit}) in {zone}"
    elif warn_high is not None and value >= warn_high:
        alert_type = "warning"
        message = f"WARNING: {parameter} high at {value}{unit} (threshold: {warn_high}{unit}) in {zone}"

    if alert_type and message:
        alert = Alert(
            alert_type=alert_type,
            category="water_quality" if system == "aquaculture" else system,
            title=f"{parameter.replace('_', ' ').title()} Alert",
            message=message,
            source_device_id=device_id,
            source_system=system,
            triggered_value=value,
            threshold_value=crit_low or warn_low or crit_high or warn_high,
            zone=zone,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    return None
