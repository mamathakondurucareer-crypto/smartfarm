"""AI-powered farm analysis endpoint using Anthropic Claude API."""

import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.config import get_settings
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import AIQueryRequest, AIQueryResponse, ConversationMessage
from backend.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Analysis"])
settings = get_settings()

# Rate limiting for AI analysis (prevent cost exhaustion attacks)
_ai_request_timestamps = defaultdict(list)  # user_id -> list of timestamps
_RATE_LIMIT_REQUESTS = 10  # requests per window
_RATE_LIMIT_WINDOW = timedelta(minutes=1)


def _check_ai_rate_limit(user_id: int) -> None:
    """Check if user has exceeded AI analysis rate limit.

    SECURITY: Limit to 10 requests per minute per user to prevent cost exhaustion attacks
    on the Anthropic API.

    Raises HTTPException(429) if limit exceeded.
    """
    now = datetime.now(timezone.utc)
    window_start = now - _RATE_LIMIT_WINDOW

    # Clean old timestamps
    _ai_request_timestamps[user_id] = [
        ts for ts in _ai_request_timestamps[user_id]
        if ts > window_start
    ]

    # Check limit
    if len(_ai_request_timestamps[user_id]) >= _RATE_LIMIT_REQUESTS:
        logger.warning(f"AI rate limit exceeded for user {user_id}")
        raise HTTPException(429, f"Too many AI requests. Max {_RATE_LIMIT_REQUESTS} per minute.")

    # Record this request
    _ai_request_timestamps[user_id].append(now)


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
    http_request: Request,
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze farm data with AI assistant.

    SECURITY: Rate limited to 10 requests/minute per user to prevent cost exhaustion attacks.
    """
    # SECURITY: Check rate limit to prevent API cost exhaustion
    _check_ai_rate_limit(current_user.id)

    if not settings.anthropic_api_key:
        logger.warning(f"AI analysis requested but ANTHROPIC_API_KEY not configured. User: {current_user.id}")
        raise HTTPException(503, "AI analysis service is not available")

    logger.info(f"AI analysis started. User: {current_user.id}, Query length: {len(request.query)}")

    try:
        import httpx
        context = build_farm_context(db)
        async with httpx.AsyncClient(timeout=60) as client:
            try:
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
                        "messages": [
                            *[{"role": m.role, "content": m.content} for m in request.conversation_history],
                            {"role": "user", "content": request.query},
                        ],
                    },
                )
                resp.raise_for_status()
            except httpx.TimeoutException as e:
                logger.error(f"AI API timeout. User: {current_user.id}. Error: {str(e)}")
                raise HTTPException(504, "AI service is taking too long to respond. Please try again.")
            except httpx.ConnectError as e:
                logger.error(f"AI API connection failed. User: {current_user.id}. Error: {str(e)}")
                raise HTTPException(503, "Could not reach AI service. Please try again.")
            except httpx.HTTPStatusError as e:
                logger.error(f"AI API error. User: {current_user.id}. Status: {e.response.status_code}. Error: {str(e)}")
                raise HTTPException(502, "AI service returned an error. Please try again.")

        data = resp.json()
        ai_text = "\n".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")

        if not ai_text:
            logger.warning(f"AI returned empty response. User: {current_user.id}")
            raise HTTPException(500, "AI returned an empty response")

        logger.info(f"AI analysis completed successfully. User: {current_user.id}, Response length: {len(ai_text)}")

        return AIQueryResponse(
            query=request.query,
            response=ai_text,
            modules_analyzed=request.context_modules,
            timestamp=datetime.now(timezone.utc),
        )

    except HTTPException:
        # Re-raise HTTP exceptions (already logged)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in AI analysis. User: {current_user.id}. Error: {str(e)}", exc_info=True)
        raise HTTPException(500, "An unexpected error occurred during analysis")


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
