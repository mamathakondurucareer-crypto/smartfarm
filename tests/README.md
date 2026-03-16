# Tests — SmartFarm OS Backend

Python backend test suite using pytest. Covers unit tests for services and functional/integration tests for all API endpoints.

## Structure

```
tests/
├── conftest.py                         # Fixtures: DB setup, test client, user roles
├── test_unit_auth_service.py           # Unit: password hashing, JWT encode/decode
├── test_unit_analytics_service.py      # Unit: KPI aggregation calculations
├── test_unit_barcode_service.py        # Unit: barcode generation and parsing
├── test_functional_health.py           # API health check endpoints
├── test_functional_auth.py             # Login, register, token refresh, role checks
├── test_functional_aquaculture.py      # Pond CRUD, fish batches, feed, water quality, harvests
├── test_functional_crops.py            # Greenhouse, vertical farm, field crop operations
├── test_functional_dashboard.py        # Dashboard KPI aggregation endpoint
├── test_functional_inventory.py        # Stock items, warehouse, batch management
├── test_functional_financial.py        # Revenue, expenses, salary, invoices
├── test_functional_pos.py              # POS sessions, transactions, daily reports
├── test_functional_packing.py          # Packing orders, barcode integration
├── test_functional_logistics.py        # Delivery routes, trips, status tracking
├── test_functional_store.py            # Store config, price rules, stock
├── test_functional_supply_chain.py     # Farm-to-store transfer operations
├── test_functional_service_requests.py # Service request lifecycle
├── test_functional_reports.py          # Report generation (PDF/Excel)
└── test_functional_activity_log.py     # Audit trail entries and queries
```

## Fixtures (conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `db` | function | Isolated SQLite session, rolls back after each test |
| `client` | function | FastAPI `TestClient` wired to test DB |
| `admin_token` | function | JWT for `admin` role user |
| `operator_token` | function | JWT for `operator` role user |
| `view_only_token` | function | JWT for `view_only` role user |
| `admin_headers` | function | `Authorization: Bearer` headers for admin |
| `operator_headers` | function | `Authorization: Bearer` headers for operator |

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_functional_aquaculture.py -v

# Unit tests only
pytest tests/test_unit_*.py -v

# With coverage
pytest tests/ --cov=backend --cov-report=term-missing

# Stop on first failure
pytest tests/ -x
```

## Test Database

Tests use an isolated in-memory SQLite database (not `smartfarm.db`). Each test function gets a fresh DB session via the `db` fixture. No test data persists between tests.

## Test Conventions

- **Functional tests** use `TestClient` to make real HTTP requests against the FastAPI app
- **Unit tests** instantiate service classes directly without HTTP overhead
- All tests assert HTTP status codes and response JSON structure
- Role-based tests verify that `view_only` users cannot mutate data (expect 403)
