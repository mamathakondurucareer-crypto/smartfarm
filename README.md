# SmartFarm OS — Integrated Smart Regenerative Farm Management System

Full-stack farm management platform for Nellore, India. Covers aquaculture, crops, poultry, IoT sensors, supply chain, retail POS, finance, AI analysis, and more.

## Architecture

```
smartfarm/
├── backend/                    # Python FastAPI backend
│   ├── main.py                 # App entry point + router registration
│   ├── database.py             # SQLAlchemy engine + session factory
│   ├── config.py               # Settings from environment variables
│   ├── models/                 # SQLAlchemy ORM models (23 files)
│   ├── routers/                # API route handlers (18 files, 24 prefixes)
│   ├── services/               # Business logic layer (5 files)
│   ├── utils/                  # Helpers and constants
│   └── seeds/seed_data.py      # Database seeding
├── mobile/                     # React Native + Expo app (iOS, Android, Web)
│   ├── App.js                  # Root component with navigation, auth guard
│   └── src/
│       ├── screens/            # 29 app screens
│       ├── components/         # Reusable UI components
│       ├── store/              # Zustand state (5 stores)
│       ├── services/           # API client layer
│       ├── hooks/              # Custom React hooks (useResponsive)
│       └── config/             # Theme, navigation, permissions
├── tests/                      # Python backend tests (pytest)
├── e2e/                        # Playwright end-to-end tests
├── scripts/                    # Setup and dev scripts
├── config/.env.example         # Environment variables template
├── docker-compose.yml          # 3-service Docker orchestration
├── Dockerfile                  # Backend container
└── requirements.txt            # Python dependencies
```

## Quick Start

### Local Development

```bash
# 1. Clone/extract and enter the project
cd smartfarm

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment
cp config/.env.example .env
# Edit .env with your settings (DB URL, JWT secret, Anthropic API key, etc.)

# 5. Seed the database
python -m backend.seeds.seed_data

# 6. Start the backend server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
# API docs: http://localhost:8000/docs

# 7. Start the mobile app (in a separate terminal)
cd mobile
npm install
npx expo start
# Web: http://localhost:8081
```

### Docker Deployment

```bash
# Build and start all services (PostgreSQL + backend + mobile web)
docker compose up --build

# Services:
#   PostgreSQL:   localhost:5433
#   Backend API:  http://localhost:8002  (docs at /docs)
#   Mobile Web:   http://localhost:8083
```

## API Modules

| Module | Base Path | Description |
|--------|-----------|-------------|
| Auth | `/api/auth` | Login, register, JWT tokens, role management |
| Dashboard | `/api/dashboard` | Aggregated KPIs, quick health, overview data |
| Aquaculture | `/api/aquaculture` | Ponds, fish batches, feed logs, water quality, harvests |
| Crops | `/api/crops` | Greenhouse, vertical farm, field crops |
| Poultry | `/api/poultry` | Flocks, ducks, egg tracking, beehives |
| Inventory | `/api/inventory` | Stock items, batches, warehouse management |
| Sensors | `/api/sensors` | IoT sensor data ingestion and queries |
| Automation | `/api/automation` | Rules, schedules, execution logs |
| Financial | `/api/financial` | Revenue, expenses, salary, invoices |
| Market | `/api/market` | Prices, orders, shipments |
| Incidents | `/api/incidents` | Disease, equipment failure, weather events |
| Production | `/api/production` | Produced, processed, shipped stock |
| Feed Production | `/api/feed` | Animal feed batch management |
| QA & Traceability | `/api/qa` | Quality audits, batch traceability |
| Compliance | `/api/compliance` | Regulatory compliance tracking |
| Nursery Orders | `/api/nursery` | Plant nursery order management |
| Drones | `/api/drones` | Drone fleet, missions, maintenance |
| AI Analysis | `/api/ai` | AI-powered farm analysis (Claude API) |
| Store Config | `/api/store` | Store setup, price rules |
| Store Stock | `/api/store/stock` | Store inventory management |
| POS | `/api/store/pos` | Point-of-sale transactions and sessions |
| Supply Chain | `/api/supply-chain` | Farm-to-store transfers |
| Packing | `/api/packing` | Packing orders with barcode generation |
| Logistics | `/api/logistics` | Delivery routes and trip tracking |
| Service Requests | `/api/service-requests` | Support ticket management |
| Activity Log | `/api/activity-logs` | Audit trail for all operations |
| Reports | `/api/reports` | Financial, farm, and store reports |

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend framework | FastAPI + Uvicorn | 0.115.0 / 0.30.0 |
| ORM | SQLAlchemy | 2.0.35 |
| Data validation | Pydantic v2 | 2.9.0 |
| Auth | python-jose + bcrypt | JWT + password hashing |
| Task scheduler | APScheduler | 3.10.4 |
| Reports | ReportLab + openpyxl | PDF and Excel export |
| AI integration | Anthropic Claude API | 0.34.0 |
| Database (dev) | SQLite | — |
| Database (prod) | PostgreSQL | 16 |
| Mobile framework | React Native + Expo | 0.83.2 / 55.0.6 |
| State management | Zustand | 4.5.5 |
| Charts | react-native-chart-kit | 6.12.0 |
| HTTP client | httpx | 0.27.0 |
| E2E testing | Playwright | 1.48.0 |
| Unit testing | pytest + Jest | — |
| Containerization | Docker + Docker Compose | 3.9 |

## Environment Variables

Copy `config/.env.example` to `.env` and set:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | SQLAlchemy DB URL (defaults to SQLite for dev) |
| `SECRET_KEY` | JWT signing secret |
| `ANTHROPIC_API_KEY` | Claude API key for AI analysis |
| `FARM_NAME` | Farm display name |
| `FARM_LOCATION` | Farm location (city, state) |
| `ALERT_*` | Sensor alert thresholds (DO, ammonia, pH, temperature, humidity) |

## Testing

See [tests/README.md](tests/README.md) for backend tests and [e2e/README.md](e2e/README.md) for E2E tests.

```bash
# Backend unit + functional tests
pytest tests/ -v

# E2E tests (requires running mobile web on :8081)
cd e2e && npx playwright test

# Mobile Jest tests
cd mobile && npm test
```

## Role-Based Access Control

17 built-in roles covering every department. Admins can override screen access per role via the **Role Management** screen; overrides persist to device storage.

| Role | Description |
|------|-------------|
| ADMIN | Full system access |
| MANAGER | All operational screens |
| SUPERVISOR | Operations + supply chain; no admin |
| WORKER | Core farm ops screens only |
| VIEWER | Read-only dashboard + reports |
| STORE_MANAGER | Store, POS, logistics, financials |
| CASHIER | POS, store view |
| PACKER | Packing, scanner, stock |
| DRIVER | Logistics, scanner |
| SCANNER | Scanner only |
| AQUA_TECH | Aquaculture, feed, water, QA, stock |
| GREENHOUSE_TECH | Greenhouse, vertical farm, nursery, QA |
| POULTRY_TECH | Poultry, feed, water, QA |
| FIELD_WORKER | Nursery, automation, compliance, water |
| QA_OFFICER | QA, compliance, all stock screens |
| FINANCE_ADMIN | Financial, reports, market, store |
| DRONE_OPS | Drones, automation, QA, field ops |

## Project Structure Details

- [backend/README.md](backend/README.md) — Backend architecture, models, routers, services
- [mobile/README.md](mobile/README.md) — Mobile app screens, state management, config
- [tests/README.md](tests/README.md) — Python test suite structure and fixtures
- [e2e/README.md](e2e/README.md) — Playwright E2E test coverage and config
