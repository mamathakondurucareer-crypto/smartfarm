"""SmartFarm OS — Main FastAPI Application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import get_settings
from backend.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print(f"🌿 {settings.app_name} v{settings.app_version} starting...")
    print(f"   Database: {settings.database_url}")
    print(f"   Farm: {settings.farm_name}")
    yield
    # Shutdown
    print("🌿 SmartFarm OS shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Integrated Smart Regenerative Farm Management System — Nellore District, AP",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# ── Health Check ──
@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "farm": settings.farm_name,
    }


# ── API Info ──
@app.get("/api/info")
def info():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "farm": {
            "name": settings.farm_name,
            "location": settings.farm_location,
            "area_acres": settings.farm_area_acres,
            "coordinates": {"lat": settings.farm_lat, "lon": settings.farm_lon},
        },
        "modules": [
            "auth", "dashboard", "aquaculture", "crops", "poultry",
            "inventory", "financial", "market", "incidents", "production",
            "sensors", "automation", "ai_analysis",
        ],
        "api_docs": "/docs",
    }
