"""SmartFarm OS — Main FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.config import get_settings
from backend.database import init_db
from backend.middleware.security import SecurityHeadersMiddleware

settings = get_settings()

# ── Rate limiter (shared instance imported by routers) ──
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate secret key on startup
    settings.effective_secret_key()
    init_db()
    db_display = settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url
    print(f"SmartFarm OS v{settings.app_version} starting — DB: {db_display}")
    print(f"Farm: {settings.farm_name}")
    yield
    print("SmartFarm OS shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Integrated Smart Regenerative Farm Management System — Nellore District, AP",
    lifespan=lifespan,
    # Disable docs in production
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# ── Rate limiter error handler ──
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Security headers (must come before CORS) ──
app.add_middleware(SecurityHeadersMiddleware)

# ── CORS ──
# Credentials require an explicit origin list — wildcard is forbidden.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Routers ──
from backend.routers.auth import router as auth_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.aquaculture import router as aquaculture_router
from backend.routers.crops import router as crops_router
from backend.routers.poultry import router as poultry_router
from backend.routers.inventory import router as inventory_router
from backend.routers.financial import router as financial_router
from backend.routers.market import router as market_router
from backend.routers.incidents_production import incidents_router, production_router
from backend.routers.sensors_automation import sensors_router, automation_router
from backend.routers.ai_analysis import router as ai_router
from backend.routers.store_config import router as store_config_router
from backend.routers.store_stock import router as store_stock_router
from backend.routers.supply_chain import router as supply_chain_router
from backend.routers.pos import router as pos_router
from backend.routers.packing import router as packing_router
from backend.routers.logistics import router as logistics_router
from backend.routers.service_requests import router as service_requests_router
from backend.routers.activity_log import router as activity_log_router
from backend.routers.reports import router as reports_router
from backend.routers.feed_production import router as feed_production_router
from backend.routers.drones import router as drones_router
from backend.routers.qa_traceability import router as qa_router
from backend.routers.compliance import router as compliance_router
from backend.routers.nursery import router as nursery_router

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(aquaculture_router)
app.include_router(crops_router)
app.include_router(poultry_router)
app.include_router(inventory_router)
app.include_router(financial_router)
app.include_router(market_router)
app.include_router(incidents_router)
app.include_router(production_router)
app.include_router(sensors_router)
app.include_router(automation_router)
app.include_router(ai_router)
app.include_router(store_config_router)
app.include_router(store_stock_router)
app.include_router(supply_chain_router)
app.include_router(pos_router)
app.include_router(packing_router)
app.include_router(logistics_router)
app.include_router(service_requests_router)
app.include_router(activity_log_router)
app.include_router(reports_router)
app.include_router(feed_production_router)
app.include_router(drones_router)
app.include_router(qa_router)
app.include_router(compliance_router)
app.include_router(nursery_router)


# ── Health Check (public — no sensitive data) ──
@app.get("/api/health")
def health():
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}


# ── API Info (public — no sensitive data) ──
@app.get("/api/info")
def info():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "farm": {
            "name": settings.farm_name,
            "location": settings.farm_location,
        },
    }
