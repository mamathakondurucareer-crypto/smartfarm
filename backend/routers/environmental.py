"""Environmental Monitoring — Ops Manual Section 17.2."""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.environmental import (
    WaterOutletLog,
    SoilCarbonLog,
    PesticideApplicationLog,
    WasteDiversionLog,
    BiodiversityLog,
    SolarNetSurplusLog,
)
from backend.schemas import (
    WaterOutletLogCreate, WaterOutletLogOut,
    SoilCarbonLogCreate, SoilCarbonLogOut,
    PesticideApplicationLogCreate, PesticideApplicationLogOut,
    WasteDiversionLogCreate, WasteDiversionLogOut,
    BiodiversityLogCreate, BiodiversityLogOut,
    SolarNetSurplusLogCreate, SolarNetSurplusLogOut,
)

router = APIRouter(prefix="/api/environmental", tags=["Environmental Monitoring"])

_WRITE_ROLES = ("admin", "manager", "supervisor", "technician")
_PESTICIDE_TARGET_KG_AI_PER_HA = 2.0
_WASTE_DIVERSION_TARGET_PCT = 95.0
_INDIA_GRID_EMISSION_FACTOR = 0.82  # kg CO2e / kWh (CEA 2023)


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Water Outlet Logs ─────────────────────────────────────────────────────────

@router.post("/water-outlet", response_model=WaterOutletLogOut)
def log_water_outlet(
    data: WaterOutletLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    entry = WaterOutletLog(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/water-outlet", response_model=list[WaterOutletLogOut])
def list_water_outlet(
    outlet_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    compliant: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterOutletLog)
    if outlet_id:
        q = q.filter(WaterOutletLog.outlet_id == outlet_id)
    if start_date:
        q = q.filter(WaterOutletLog.log_date >= start_date)
    if end_date:
        q = q.filter(WaterOutletLog.log_date <= end_date)
    if compliant is not None:
        q = q.filter(WaterOutletLog.compliant == compliant)
    return q.order_by(WaterOutletLog.log_date.desc()).all()


@router.get("/water-outlet/trends")
def water_outlet_trends(
    outlet_id: Optional[str] = None,
    weeks: int = Query(default=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Weekly average BOD, TSS, pH over the past N weeks."""
    since = date.today() - timedelta(weeks=weeks)
    q = db.query(WaterOutletLog).filter(WaterOutletLog.log_date >= since)
    if outlet_id:
        q = q.filter(WaterOutletLog.outlet_id == outlet_id)
    logs = q.order_by(WaterOutletLog.log_date).all()

    non_compliant = sum(1 for l in logs if l.compliant is False)
    return {
        "weeks_back": weeks,
        "total_readings": len(logs),
        "non_compliant_count": non_compliant,
        "avg_bod_mg_l": _safe_avg([l.bod_mg_l for l in logs]),
        "avg_tss_mg_l": _safe_avg([l.tss_mg_l for l in logs]),
        "avg_ph": _safe_avg([l.ph for l in logs]),
        "readings": [
            {
                "log_date": l.log_date.isoformat(),
                "outlet_id": l.outlet_id,
                "bod_mg_l": l.bod_mg_l,
                "tss_mg_l": l.tss_mg_l,
                "ph": l.ph,
                "compliant": l.compliant,
            }
            for l in logs
        ],
    }


# ── Soil Carbon Logs ──────────────────────────────────────────────────────────

@router.post("/soil-carbon", response_model=SoilCarbonLogOut)
def log_soil_carbon(
    data: SoilCarbonLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    entry = SoilCarbonLog(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/soil-carbon", response_model=list[SoilCarbonLogOut])
def list_soil_carbon(
    field_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SoilCarbonLog)
    if field_id:
        q = q.filter(SoilCarbonLog.field_id == field_id)
    return q.order_by(SoilCarbonLog.log_date.desc()).all()


@router.get("/soil-carbon/trend")
def soil_carbon_trend(
    field_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quarterly SOC trend for a field with year-over-year delta and target tracking."""
    logs = (
        db.query(SoilCarbonLog)
        .filter(SoilCarbonLog.field_id == field_id)
        .order_by(SoilCarbonLog.log_date)
        .all()
    )
    if not logs:
        raise HTTPException(404, f"No soil carbon records for field '{field_id}'")

    readings = [{"log_date": l.log_date.isoformat(), "soc_pct": l.soc_pct} for l in logs]

    # Year-over-year delta: compare first vs last reading in each year pair
    yoy_delta = None
    if len(logs) >= 2:
        yoy_delta = round(logs[-1].soc_pct - logs[0].soc_pct, 4)

    # Annualised rate (simple linear)
    annual_rate = None
    if len(logs) >= 2:
        days_span = (logs[-1].log_date - logs[0].log_date).days
        if days_span > 0:
            annual_rate = round((yoy_delta / days_span) * 365, 4)

    return {
        "field_id": field_id,
        "field_name": logs[0].field_name,
        "target_annual_increase_pct": 0.2,
        "readings_count": len(logs),
        "first_reading": readings[0],
        "latest_reading": readings[-1],
        "total_change_pct": yoy_delta,
        "annualised_rate_pct": annual_rate,
        "on_track": annual_rate is not None and annual_rate >= 0.2,
        "readings": readings,
    }


# ── Pesticide Application Logs ────────────────────────────────────────────────

@router.post("/pesticide-applications", response_model=PesticideApplicationLogOut)
def log_pesticide_application(
    data: PesticideApplicationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    payload = data.model_dump()
    if data.area_ha > 0:
        payload["ai_per_ha"] = round(data.quantity_kg / data.area_ha, 4)
    entry = PesticideApplicationLog(**payload)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/pesticide-applications", response_model=list[PesticideApplicationLogOut])
def list_pesticide_applications(
    field_id: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PesticideApplicationLog)
    if field_id:
        q = q.filter(PesticideApplicationLog.field_id == field_id)
    if year:
        q = q.filter(extract("year", PesticideApplicationLog.application_date) == year)
    return q.order_by(PesticideApplicationLog.application_date.desc()).all()


@router.get("/pesticide-applications/summary")
def pesticide_summary(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Per-field AI load (kg/ha) for the year vs the 2 kg AI/ha/year target."""
    target_year = year or date.today().year
    logs = (
        db.query(PesticideApplicationLog)
        .filter(extract("year", PesticideApplicationLog.application_date) == target_year)
        .all()
    )

    by_field: dict = {}
    for l in logs:
        if l.field_id not in by_field:
            by_field[l.field_id] = {
                "field_id": l.field_id,
                "field_name": l.field_name,
                "total_quantity_kg": 0.0,
                "total_area_ha": 0.0,
                "applications": 0,
            }
        by_field[l.field_id]["total_quantity_kg"] += l.quantity_kg or 0
        by_field[l.field_id]["total_area_ha"] = max(
            by_field[l.field_id]["total_area_ha"], l.area_ha or 0
        )
        by_field[l.field_id]["applications"] += 1

    results = []
    for f in by_field.values():
        ai_per_ha = round(f["total_quantity_kg"] / f["total_area_ha"], 4) if f["total_area_ha"] else None
        results.append({
            **f,
            "ai_per_ha_ytd": ai_per_ha,
            "target_kg_ai_per_ha": _PESTICIDE_TARGET_KG_AI_PER_HA,
            "within_target": ai_per_ha is not None and ai_per_ha <= _PESTICIDE_TARGET_KG_AI_PER_HA,
        })

    return {
        "year": target_year,
        "target_kg_ai_per_ha": _PESTICIDE_TARGET_KG_AI_PER_HA,
        "total_applications": len(logs),
        "fields": results,
    }


# ── Waste Diversion Logs ──────────────────────────────────────────────────────

@router.post("/waste-diversion", response_model=WasteDiversionLogOut)
def log_waste_diversion(
    data: WasteDiversionLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    payload = data.model_dump()
    if data.total_waste_kg > 0:
        rate = round((data.diverted_kg / data.total_waste_kg) * 100, 2)
        payload["diversion_rate_pct"] = rate
        payload["meets_target"] = rate >= _WASTE_DIVERSION_TARGET_PCT
    entry = WasteDiversionLog(**payload)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/waste-diversion", response_model=list[WasteDiversionLogOut])
def list_waste_diversion(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WasteDiversionLog)
    if year:
        q = q.filter(extract("year", WasteDiversionLog.log_date) == year)
    return q.order_by(WasteDiversionLog.log_date.desc()).all()


@router.get("/waste-diversion/monthly")
def waste_diversion_monthly(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Monthly diversion rates for the year with target achievement count."""
    target_year = year or date.today().year
    logs = (
        db.query(WasteDiversionLog)
        .filter(extract("year", WasteDiversionLog.log_date) == target_year)
        .order_by(WasteDiversionLog.log_date)
        .all()
    )
    months_meeting_target = sum(1 for l in logs if l.meets_target)
    avg_rate = _safe_avg([l.diversion_rate_pct for l in logs])
    return {
        "year": target_year,
        "target_pct": _WASTE_DIVERSION_TARGET_PCT,
        "months_recorded": len(logs),
        "months_meeting_target": months_meeting_target,
        "average_diversion_rate_pct": avg_rate,
        "monthly": [
            {
                "month": l.log_date.strftime("%Y-%m"),
                "total_waste_kg": l.total_waste_kg,
                "diverted_kg": l.diverted_kg,
                "diversion_rate_pct": l.diversion_rate_pct,
                "meets_target": l.meets_target,
            }
            for l in logs
        ],
    }


# ── Biodiversity Logs ─────────────────────────────────────────────────────────

@router.post("/biodiversity", response_model=BiodiversityLogOut)
def log_biodiversity(
    data: BiodiversityLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    entry = BiodiversityLog(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/biodiversity", response_model=list[BiodiversityLogOut])
def list_biodiversity(
    survey_type: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(BiodiversityLog)
    if survey_type:
        q = q.filter(BiodiversityLog.survey_type == survey_type)
    if location:
        q = q.filter(BiodiversityLog.location.ilike(f"%{location}%"))
    return q.order_by(BiodiversityLog.survey_date.desc()).all()


# ── Solar Net Surplus Logs ────────────────────────────────────────────────────

@router.post("/solar-surplus", response_model=SolarNetSurplusLogOut)
def log_solar_surplus(
    data: SolarNetSurplusLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    # Upsert-style: prevent duplicate dates
    existing = db.query(SolarNetSurplusLog).filter(SolarNetSurplusLog.log_date == data.log_date).first()
    if existing:
        raise HTTPException(409, f"Solar surplus log already exists for {data.log_date}")
    payload = data.model_dump()
    net = round(data.generation_kwh - data.consumption_kwh, 3)
    payload["net_surplus_kwh"] = net
    payload["carbon_offset_kg"] = round(max(net, 0) * _INDIA_GRID_EMISSION_FACTOR, 3)
    entry = SolarNetSurplusLog(**payload)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/solar-surplus", response_model=list[SolarNetSurplusLogOut])
def list_solar_surplus(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SolarNetSurplusLog)
    if start_date:
        q = q.filter(SolarNetSurplusLog.log_date >= start_date)
    if end_date:
        q = q.filter(SolarNetSurplusLog.log_date <= end_date)
    return q.order_by(SolarNetSurplusLog.log_date.desc()).all()


@router.get("/solar-surplus/carbon-report")
def solar_carbon_report(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Annual carbon offset report from solar net surplus — for carbon reporting."""
    target_year = year or date.today().year
    logs = (
        db.query(SolarNetSurplusLog)
        .filter(extract("year", SolarNetSurplusLog.log_date) == target_year)
        .order_by(SolarNetSurplusLog.log_date)
        .all()
    )
    total_gen = sum(l.generation_kwh for l in logs)
    total_con = sum(l.consumption_kwh for l in logs)
    total_surplus = sum((l.net_surplus_kwh or 0) for l in logs)
    total_export = sum((l.grid_export_kwh or 0) for l in logs)
    total_offset = sum((l.carbon_offset_kg or 0) for l in logs)

    monthly: dict = {}
    for l in logs:
        key = l.log_date.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {"generation_kwh": 0, "consumption_kwh": 0, "net_surplus_kwh": 0, "carbon_offset_kg": 0}
        monthly[key]["generation_kwh"] += l.generation_kwh
        monthly[key]["consumption_kwh"] += l.consumption_kwh
        monthly[key]["net_surplus_kwh"] += l.net_surplus_kwh or 0
        monthly[key]["carbon_offset_kg"] += l.carbon_offset_kg or 0

    return {
        "year": target_year,
        "days_recorded": len(logs),
        "total_generation_kwh": round(total_gen, 2),
        "total_consumption_kwh": round(total_con, 2),
        "total_net_surplus_kwh": round(total_surplus, 2),
        "total_grid_export_kwh": round(total_export, 2),
        "total_carbon_offset_kg": round(total_offset, 2),
        "total_carbon_offset_tonnes": round(total_offset / 1000, 4),
        "grid_emission_factor_kg_per_kwh": _INDIA_GRID_EMISSION_FACTOR,
        "monthly_breakdown": {k: {p: round(v, 2) for p, v in mv.items()} for k, mv in monthly.items()},
    }


# ── Environmental Summary ─────────────────────────────────────────────────────

@router.get("/summary")
def environmental_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cross-module environmental KPI snapshot."""
    today = date.today()
    year = today.year

    # Water outlet compliance (last 30 days)
    thirty_ago = today - timedelta(days=30)
    recent_water = db.query(WaterOutletLog).filter(WaterOutletLog.log_date >= thirty_ago).all()
    water_compliant = sum(1 for l in recent_water if l.compliant is True)
    water_total = len(recent_water)

    # Latest SOC reading per field
    soc_fields = db.query(SoilCarbonLog.field_id).distinct().count()

    # YTD pesticide
    ytd_pesticide = (
        db.query(PesticideApplicationLog)
        .filter(extract("year", PesticideApplicationLog.application_date) == year)
        .count()
    )

    # Latest waste diversion
    latest_waste = (
        db.query(WasteDiversionLog)
        .order_by(WasteDiversionLog.log_date.desc())
        .first()
    )

    # YTD solar
    ytd_solar = (
        db.query(SolarNetSurplusLog)
        .filter(extract("year", SolarNetSurplusLog.log_date) == year)
        .all()
    )
    ytd_carbon_offset = sum((l.carbon_offset_kg or 0) for l in ytd_solar)

    # Last biodiversity survey
    last_bio = (
        db.query(BiodiversityLog)
        .order_by(BiodiversityLog.survey_date.desc())
        .first()
    )

    return {
        "as_of": today.isoformat(),
        "water_outlet": {
            "readings_last_30d": water_total,
            "compliant": water_compliant,
            "compliance_rate_pct": round(water_compliant / water_total * 100, 1) if water_total else None,
        },
        "soil_carbon": {
            "fields_monitored": soc_fields,
            "annual_target_pct": 0.2,
        },
        "pesticide": {
            "ytd_applications": ytd_pesticide,
            "target_kg_ai_per_ha": _PESTICIDE_TARGET_KG_AI_PER_HA,
        },
        "waste_diversion": {
            "latest_month": latest_waste.log_date.isoformat() if latest_waste else None,
            "latest_rate_pct": latest_waste.diversion_rate_pct if latest_waste else None,
            "meets_target": latest_waste.meets_target if latest_waste else None,
            "target_pct": _WASTE_DIVERSION_TARGET_PCT,
        },
        "solar": {
            "ytd_days_logged": len(ytd_solar),
            "ytd_carbon_offset_kg": round(ytd_carbon_offset, 2),
            "ytd_carbon_offset_tonnes": round(ytd_carbon_offset / 1000, 4),
        },
        "biodiversity": {
            "last_survey_date": last_bio.survey_date.isoformat() if last_bio else None,
            "last_survey_type": last_bio.survey_type if last_bio else None,
            "last_species_count": last_bio.species_count if last_bio else None,
        },
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe_avg(values: list) -> Optional[float]:
    filtered = [v for v in values if v is not None]
    return round(sum(filtered) / len(filtered), 3) if filtered else None
