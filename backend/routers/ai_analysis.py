"""AI-powered farm analysis endpoint using Anthropic Claude API."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.config import get_settings
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import AIQueryRequest, AIQueryResponse
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/ai", tags=["AI Analysis"])
settings = get_settings()


def build_farm_context(db: Session) -> str:
    """Build comprehensive farm context from live database."""
    svc = AnalyticsService(db)
    kpis = svc.get_dashboard_kpis()

    from backend.models.aquaculture import Pond, FishBatch, WaterQualityLog
    from backend.models.crop import GreenhouseCrop, VerticalFarmBatch
    from backend.models.poultry import PoultryFlock, EggCollection
    from backend.models.sensor import Alert
    from backend.models.inventory import InventoryItem
    from backend.models.incident import Incident

    ponds = db.query(Pond).filter(Pond.is_active == True).all()
    pond_lines = []
    for p in ponds:
        batches = db.query(FishBatch).filter(FishBatch.pond_id == p.id, FishBatch.status == "growing").all()
        wq = db.query(WaterQualityLog).filter(WaterQualityLog.pond_id == p.id).order_by(WaterQualityLog.recorded_at.desc()).first()
        stock = sum(b.current_count for b in batches)
        biomass = sum(b.current_count * b.current_avg_weight_g / 1000 for b in batches)
        wq_str = f"DO={wq.dissolved_oxygen},pH={wq.ph},Temp={wq.water_temperature},NH3={wq.ammonia}" if wq else "No data"
        pond_lines.append(f"{p.pond_code}({p.pond_type}): Stock={stock}, Biomass={biomass:.1f}kg, WQ=[{wq_str}]")

    gh_crops = db.query(GreenhouseCrop).filter(GreenhouseCrop.status == "active").all()
    gh_str = "; ".join(f"{c.crop_name}: {c.growth_stage}, Health={c.health_score}%, Yield={c.actual_yield_kg}/{c.target_yield_kg}kg" for c in gh_crops)

    vf = db.query(VerticalFarmBatch).filter(VerticalFarmBatch.status == "growing").all()
    vf_str = "; ".join(f"{v.crop_name}: Day{v.current_day}/{v.cycle_days}, Health={v.health_score}%" for v in vf)

    flock = db.query(PoultryFlock).filter(PoultryFlock.status == "laying").first()
    poultry_str = f"Hens={flock.current_count}, LayRate={flock.lay_rate_pct}%" if flock else "No active flock"

    active_alerts = db.query(Alert).filter(Alert.resolved == False).order_by(Alert.created_at.desc()).limit(10).all()
    alert_str = "; ".join(f"[{a.alert_type}] {a.message}" for a in active_alerts) or "No active alerts"

    low_items = db.query(InventoryItem).filter(
        InventoryItem.current_stock <= InventoryItem.reorder_point, InventoryItem.is_active == True
    ).all()
    low_str = "; ".join(f"{i.name}: {i.current_stock}/{i.reorder_point} {i.unit}" for i in low_items) or "All adequate"

    incidents = db.query(Incident).filter(Incident.status.in_(["open", "investigating"])).all()
    inc_str = "; ".join(f"[{i.severity}] {i.title}" for i in incidents) or "None"

    return f"""SMARTFARM OS — LIVE DATABASE CONTEXT
Farm: Nellore Integrated Smart Farm, AP, India | 5 Acres

FINANCIAL KPIs: Revenue=₹{kpis['financial']['revenue']:.0f}, Expenses=₹{kpis['financial']['expenses']:.0f}, Profit=₹{kpis['financial']['profit']:.0f}, Margin={kpis['financial']['margin_pct']}%

AQUACULTURE ({kpis['aquaculture']['active_ponds']} ponds, {kpis['aquaculture']['total_stock']} fish):
{chr(10).join(pond_lines)}

GREENHOUSE: {gh_str or 'No active crops'}
VERTICAL FARM: {vf_str or 'No active batches'}
POULTRY: {poultry_str}

ACTIVE ALERTS: {alert_str}
LOW STOCK ITEMS: {low_str}
OPEN INCIDENTS: {inc_str}
PENDING ORDERS: {kpis['operations']['pending_orders']}"""


@router.post("/analyze", response_model=AIQueryResponse)
async def analyze(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not settings.anthropic_api_key:
        raise HTTPException(503, "AI analysis service is not available")

    try:
        import httpx
        context = build_farm_context(db)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2000,
                    "system": f"""You are the AI Farm Analyst for SmartFarm OS. You have access to live operational data from the farm's database. Provide expert agricultural analysis with specific, actionable recommendations. Use data-driven insights with exact numbers from the context. Format with clear sections and priorities. Use ₹ for currency.

{context}""",
                    "messages": [{"role": "user", "content": request.query}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            ai_text = "\n".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")

        return AIQueryResponse(
            query=request.query,
            response=ai_text,
            modules_analyzed=request.context_modules,
            timestamp=datetime.now(timezone.utc),
        )
    except httpx.HTTPStatusError:
        raise HTTPException(502, "AI service error — please try again")
    except Exception:
        raise HTTPException(500, "AI analysis failed")


@router.get("/quick-health")
def quick_health_check(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Non-AI quick health summary from database."""
    svc = AnalyticsService(db)
    kpis = svc.get_dashboard_kpis()

    from backend.models.sensor import Alert
    critical_alerts = db.query(Alert).filter(Alert.alert_type == "critical", Alert.resolved == False).count()

    health_score = 100
    issues = []
    if critical_alerts > 0:
        health_score -= critical_alerts * 15
        issues.append(f"{critical_alerts} critical alert(s) active")
    if kpis["operations"]["low_stock_items"] > 3:
        health_score -= 10
        issues.append(f"{kpis['operations']['low_stock_items']} items below reorder point")
    if kpis["operations"]["open_incidents"] > 0:
        health_score -= kpis["operations"]["open_incidents"] * 5
        issues.append(f"{kpis['operations']['open_incidents']} open incident(s)")

    return {
        "overall_health_score": max(0, health_score),
        "rating": "Excellent" if health_score >= 90 else "Good" if health_score >= 70 else "Fair" if health_score >= 50 else "Critical",
        "kpis": kpis,
        "issues": issues,
    }
