# E2E Tests — SmartFarm OS

Playwright end-to-end tests for the mobile web app. Tests run against the Expo web build on `http://localhost:8081`.

## Structure

```
e2e/
├── playwright.config.js            # Browser config, base URL, timeouts, reporters
└── tests/
    ├── auth/
    │   └── login.spec.js           # Login form, JWT storage, logout
    ├── farm/
    │   ├── aquaculture.spec.js     # Pond list, fish batch creation, water quality
    │   ├── crops.spec.js           # Greenhouse, vertical farm, field crop screens
    │   ├── poultry.spec.js         # Flock management, egg tracking
    │   └── energy_automation.spec.js # Energy monitor, automation rules
    ├── finance/
    │   └── market_financial.spec.js # Market prices, revenue/expense entry
    ├── stock/
    │   └── scanner.spec.js         # Barcode scanner screen
    ├── store/
    │   ├── pos.spec.js             # POS session, cart, transaction flow
    │   └── stock.spec.js           # Store stock view and management
    ├── admin/
    │   ├── users.spec.js           # User list, role management
    │   ├── ai.spec.js              # AI analysis screen
    │   └── reports.spec.js         # Report generation and download
    └── edge_cases/
        ├── unauthorized.spec.js    # Unauthenticated redirect behavior
        └── form_validation.spec.js # Required fields, invalid input handling
```

## Configuration

| Setting | Value |
|---------|-------|
| Base URL | `http://localhost:8081` |
| Browsers | Chromium, WebKit (Safari) |
| Timeout | 30 seconds per test |
| Expect timeout | 8 seconds |
| Parallel workers | 2 (configurable for CI) |
| Mode | Headless |
| On failure | Screenshot + video retained, trace recorded |

## Running Tests

```bash
# Install Playwright browsers (first time)
cd e2e
npx playwright install

# Run all tests (requires mobile web running on :8081 and backend on :8000)
npx playwright test

# Run specific file
npx playwright test tests/farm/aquaculture.spec.js

# Run with headed browser (visible)
npx playwright test --headed

# Show HTML report after run
npx playwright show-report

# Run for a specific browser
npx playwright test --project=chromium
npx playwright test --project=webkit
```

## Prerequisites

Before running E2E tests, ensure both services are running:

```bash
# Terminal 1 — backend
uvicorn backend.main:app --port 8000

# Terminal 2 — mobile web
cd mobile && npx expo start --web

# Terminal 3 — run tests
cd e2e && npx playwright test
```

Or use Docker Compose which starts everything:

```bash
docker compose up
cd e2e && npx playwright test
# Backend on :8002, mobile web on :8083 — update BASE_URL if using Docker ports
```

## Artifacts

Test artifacts are saved to `e2e/test-results/`:
- Screenshots on failure
- Videos retained on failure
- Playwright traces for debugging

View the HTML report:
```bash
npx playwright show-report
```
