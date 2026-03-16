# Backend — SmartFarm OS

Python FastAPI backend with SQLAlchemy ORM, JWT auth, AI analysis, and background scheduling.

## Directory Structure

```
backend/
├── main.py                         # FastAPI app, router registration, CORS, lifespan
├── database.py                     # SQLAlchemy engine + session factory
├── config.py                       # Settings loaded from environment (.env)
├── models/                         # SQLAlchemy ORM models
│   ├── base.py                     # TimestampMixin, SoftDeleteMixin
│   ├── user.py                     # User, Role, Employee, Attendance
│   ├── aquaculture.py              # Pond, FishBatch, FeedLog, WaterQualityLog, FishHarvest, CrabBatch
│   ├── crop.py                     # Greenhouse, VerticalFarm, FieldCrop, Harvest
│   ├── poultry.py                  # Flock, Duck, Egg, BeehiveLog
│   ├── inventory.py                # InventoryItem, InventoryBatch, Warehouse
│   ├── sensor.py                   # SensorReading, SensorAlert
│   ├── automation.py               # AutomationRule, ExecutionLog
│   ├── financial.py                # Revenue, Expense, Salary, Invoice
│   ├── market.py                   # MarketPrice, Order, Shipment
│   ├── incident.py                 # Incident, IncidentLog
│   ├── production.py               # ProductionBatch, ShippedStock
│   ├── store.py                    # StoreConfig, PriceRule
│   ├── retail.py                   # ProductCatalog
│   ├── supply_chain.py             # FarmSupplyTransfer
│   ├── packing.py                  # PackingOrder
│   ├── logistics.py                # DeliveryRoute, DeliveryTrip
│   ├── service_request.py          # ServiceRequest
│   └── activity_log.py             # ActivityLog
├── routers/                        # API route handlers
│   ├── auth.py                     # /api/auth — login, register, JWT, roles
│   ├── dashboard.py                # /api/dashboard — aggregated KPIs
│   ├── aquaculture.py              # /api/aquaculture — ponds, fish, feed, harvests
│   ├── crops.py                    # /api/crops — greenhouse, vertical farm, field
│   ├── poultry.py                  # /api/poultry — flocks, ducks, eggs, bees
│   ├── inventory.py                # /api/inventory — stock, warehouse
│   ├── sensors_automation.py       # /api/sensors + /api/automation
│   ├── financial.py                # /api/financial — revenue, expenses, salary
│   ├── market.py                   # /api/market — prices, orders, shipments
│   ├── incidents_production.py     # /api/incidents + /api/production
│   ├── ai_analysis.py              # /api/ai — AI-powered analysis (Claude API)
│   ├── store_config.py             # /api/store — store setup, price rules
│   ├── store_stock.py              # /api/store/stock — store inventory
│   ├── pos.py                      # /api/store/pos — POS transactions
│   ├── supply_chain.py             # /api/supply-chain — farm-to-store transfers
│   ├── packing.py                  # /api/packing — packing orders + barcodes
│   ├── logistics.py                # /api/logistics — delivery routes + trips
│   ├── service_requests.py         # /api/service-requests — support tickets
│   ├── activity_log.py             # /api/activity-logs — audit trail
│   └── reports.py                  # /api/reports — report generation
├── services/                       # Business logic
│   ├── auth_service.py             # Password hashing, JWT creation + verification
│   ├── analytics_service.py        # Data aggregation, KPI calculations
│   ├── alert_service.py            # Sensor threshold monitoring + alerting
│   ├── activity_log_service.py     # Activity logging helpers
│   └── barcode_service.py          # Barcode generation and scanning
├── utils/
│   ├── helpers.py                  # Common utility functions
│   └── constants.py                # Farm constants and alert thresholds
└── seeds/
    └── seed_data.py                # Initial database population
```

## Models

All models extend `Base` from `base.py` which provides:
- `id` — Integer primary key
- `created_at`, `updated_at` — Auto-managed timestamps
- `is_deleted`, `deleted_at` — Soft delete support

## Routers

Routes are registered in `main.py`. Each router uses `APIRouter` with a prefix and tags. Authentication is enforced via `Depends(get_current_user)` dependency on protected endpoints.

**Role-based access:**
- `admin` — full access
- `operator` — read/write farm operations
- `view_only` — read-only

## Services

| Service | Responsibility |
|---------|---------------|
| `auth_service` | bcrypt hashing, JWT encode/decode, user lookup |
| `analytics_service` | Aggregate sensor, financial, and production KPIs |
| `alert_service` | Compare readings to thresholds, create `SensorAlert` records |
| `activity_log_service` | Write `ActivityLog` entries for auditable actions |
| `barcode_service` | Generate QR/barcodes for packing orders, parse on scan |

## Configuration

Settings are loaded via `config.py` using `pydantic-settings`. All values can be overridden in `.env`:

```
DATABASE_URL=sqlite:///./smartfarm.db
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ANTHROPIC_API_KEY=sk-ant-...
FARM_NAME=SmartFarm Nellore
```

## Running

```bash
# Development (SQLite)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Production (PostgreSQL via Docker)
docker compose up backend
```

API docs available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.
