# 🌿 SmartFarm OS — Integrated Smart Regenerative Farm Management System

## Complete Backend + Frontend for Nellore Smart Farm Project

### Architecture
```
smartfarm/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── database.py                # SQLAlchemy engine + session factory
│   ├── config.py                  # App configuration + environment
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base model with audit fields
│   │   ├── user.py                # Users, roles, HR
│   │   ├── aquaculture.py         # Ponds, fish stock, feed, harvests
│   │   ├── crop.py                # Greenhouse, vertical farm, field crops
│   │   ├── poultry.py             # Hens, ducks, eggs, bees
│   │   ├── inventory.py           # All farm inventory + warehouse
│   │   ├── sensor.py              # IoT sensor readings
│   │   ├── automation.py          # Automation rules + execution logs
│   │   ├── financial.py           # Revenue, expenses, salary, invoices
│   │   ├── market.py              # Market prices, orders, shipments
│   │   ├── incident.py            # Disease, equipment failure, weather events
│   │   └── production.py          # Stock produced, processed, shipped
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── aquaculture.py
│   │   ├── crop.py
│   │   ├── poultry.py
│   │   ├── inventory.py
│   │   ├── sensor.py
│   │   ├── financial.py
│   │   ├── market.py
│   │   ├── incident.py
│   │   └── production.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication + JWT
│   │   ├── dashboard.py           # Dashboard aggregation
│   │   ├── aquaculture.py         # Pond CRUD, feed logs, harvests
│   │   ├── crops.py               # Crop management
│   │   ├── poultry.py             # Poultry + duck + bees
│   │   ├── inventory.py           # Inventory management
│   │   ├── sensors.py             # Sensor data ingestion + queries
│   │   ├── automation.py          # Automation workflows
│   │   ├── financial.py           # Finance, salary, HR
│   │   ├── market.py              # Market data + shipments
│   │   ├── incidents.py           # Incident tracking
│   │   ├── production.py          # Production + shipping
│   │   └── ai_analysis.py         # AI-powered analysis endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Password hashing, JWT
│   │   ├── analytics_service.py   # Data aggregation + KPI calculation
│   │   ├── alert_service.py       # Threshold monitoring + alerts
│   │   ├── ai_service.py          # AI analysis engine
│   │   ├── report_service.py      # Report generation
│   │   └── scheduler_service.py   # Background task scheduler
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py             # Common utilities
│   │   └── constants.py           # Farm constants + thresholds
│   └── seeds/
│       └── seed_data.py           # Initial database seeding
├── frontend/
│   └── SmartFarmOS.jsx            # React dashboard (artifact)
├── scripts/
│   ├── setup.sh                   # One-click setup script
│   ├── run_dev.sh                 # Development runner
│   └── backup_db.py               # Database backup utility
├── config/
│   └── .env.example               # Environment variables template
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker deployment
├── Dockerfile                     # Backend container
└── README.md                      # This file
```

### Quick Start
```bash
# 1. Clone or extract the project
cd smartfarm

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp config/.env.example .env
# Edit .env with your settings

# 5. Initialize database + seed data
python -m backend.seeds.seed_data

# 6. Run the server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# API Docs: http://localhost:8000/docs
# Dashboard: http://localhost:8000 (serves frontend)
```

### API Modules
| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | `/api/auth/*` | Login, register, JWT tokens, roles |
| Dashboard | `/api/dashboard/*` | Aggregated KPIs, overview data |
| Aquaculture | `/api/aquaculture/*` | Ponds, fish stock, feed, water quality, harvests |
| Crops | `/api/crops/*` | Greenhouse, vertical farm, field crops |
| Poultry | `/api/poultry/*` | Hens, ducks, bees, egg tracking |
| Inventory | `/api/inventory/*` | Stock items, warehouse, procurement |
| Sensors | `/api/sensors/*` | IoT data ingestion and queries |
| Automation | `/api/automation/*` | Rules, schedules, execution logs |
| Financial | `/api/financial/*` | Revenue, expenses, salary, invoices |
| Market | `/api/market/*` | Prices, orders, shipments |
| Incidents | `/api/incidents/*` | Disease, failure, weather events |
| Production | `/api/production/*` | Produced, processed, shipped stock |
| AI Analysis | `/api/ai/*` | AI-powered farm analysis |
| HR | `/api/hr/*` | Employees, attendance, payroll |

### Technology Stack
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Auth**: JWT (python-jose) + bcrypt password hashing
- **Frontend**: React 18, Recharts, Lucide Icons
- **AI**: Anthropic Claude API integration
- **Deployment**: Docker + Docker Compose
