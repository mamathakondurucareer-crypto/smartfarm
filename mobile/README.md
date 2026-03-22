# Mobile — SmartFarm OS

React Native + Expo app supporting iOS, Android, and Web. 29 screens covering all farm management domains. Adapts layout for mobile, tablet, and desktop automatically.

## Directory Structure

```
mobile/
├── App.js                          # Root component: navigation, auth guard, error boundary
├── app.json                        # Expo configuration
├── package.json                    # npm dependencies and scripts
├── babel.config.js                 # Babel config (Expo preset)
├── metro.config.js                 # Metro bundler config
├── jest.setup.js                   # Jest + Testing Library setup
├── Dockerfile                      # Multi-stage build: Expo → Nginx static web
├── src/
│   ├── screens/                    # 29 JSX screen components + companion .styles.js files
│   ├── components/
│   │   ├── layout/                 # ScreenWrapper, DrawerContent (sidebar/overlay)
│   │   └── ui/                     # Card, Badge, SectionHeader, DataTable, etc.
│   ├── store/                      # Zustand state stores (5)
│   ├── services/                   # API client (api.js)
│   ├── context/                    # NavigationContext (custom router)
│   ├── config/                     # Theme, navigation registry, permissions
│   ├── hooks/                      # useResponsive (breakpoint detection)
│   ├── styles/                     # Shared stylesheets (common.js)
│   └── data/                       # Default/fallback state data
├── __tests__/                      # Jest test files
├── __mocks__/                      # Jest mocks for native modules
└── assets/                         # Images and static assets
```

## Responsive Layout

The app uses three layout breakpoints detected via `useResponsive()`:

| Breakpoint | Width | Layout |
|-----------|-------|--------|
| Mobile | < 768 px | Overlay drawer + bottom tab bar (4 tabs + More) |
| Tablet | 768–1023 px | Permanent 200 px sidebar, no bottom bar |
| Desktop | ≥ 1024 px | Permanent 240 px sidebar, no bottom bar |

Bottom tab candidates: Dashboard, Aquaculture, Store, Financial, Service Requests — filtered by role, first 4 accessible shown.

## Screens (29)

### Farm Operations
| Screen | Key | File | Description |
|--------|-----|------|-------------|
| Dashboard | `Dashboard` | `DashboardScreen.jsx` | KPI overview, quick stats |
| Aquaculture | `Aquaculture` | `AquacultureScreen.jsx` | Ponds, fish batches, water quality, harvests |
| Greenhouse | `Greenhouse` | `GreenhouseScreen.jsx` | Greenhouse crop management |
| Vertical Farm | `VerticalFarm` | `VerticalFarmScreen.jsx` | Vertical farming units |
| Poultry & Duck | `Poultry` | `PoultryScreen.jsx` | Flocks, ducks, eggs, beehives |
| Water System | `Water` | `WaterScreen.jsx` | Water management |
| Solar Energy | `Energy` | `EnergyScreen.jsx` | Energy monitoring |
| Automation | `Automation` | `AutomationScreen.jsx` | Automation rules and schedules |
| Nursery & Bees | `Nursery` | `NurseryScreen.jsx` | Nursery/seedling and apiary |
| Nursery Orders | `NurseryBE` | `NurseryBackendScreen.jsx` | Plant nursery order management (backend) |
| Feed Production | `FeedProduction` | `FeedProductionScreen.jsx` | Animal feed batch management |
| Drones | `Drones` | `DroneScreen.jsx` | Drone fleet, missions, maintenance logs |

### Quality & Compliance
| Screen | Key | File | Description |
|--------|-----|------|-------------|
| QA & Traceability | `QA` | `QAScreen.jsx` | Quality audits, batch traceability |
| Compliance | `Compliance` | `ComplianceScreen.jsx` | Regulatory compliance tracking |

### Stock & Supply Chain
| Screen | Key | File | Description |
|--------|-----|------|-------------|
| Stock Produced | `StockProduced` | `StockProducedScreen.jsx` | Production batches |
| Stock Sales | `StockSales` | `StockSalesScreen.jsx` | Sales and shipments |
| Packing | `Packing` | `PackingScreen.jsx` | Packing order management with barcodes |
| Scan Barcode | `Scanner` | `ScannerScreen.jsx` | Barcode/QR scanning |
| Logistics | `Logistics` | `LogisticsScreen.jsx` | Delivery routes and trips |

### Store & Retail
| Screen | Key | File | Description |
|--------|-----|------|-------------|
| Store | `Store` | `StoreScreen.jsx` | Store configuration and stock |
| Point of Sale | `POS` | `POSScreen.jsx` | POS transactions and sessions |
| Markets | `Market` | `MarketScreen.jsx` | Market prices and orders |

### Finance
| Screen | Key | File | Description |
|--------|-----|------|-------------|
| Financials | `Financial` | `FinancialScreen.jsx` | Revenue, expenses, salary |
| Reports | `Reports` | `ReportsScreen.jsx` | Report generation and export |

### Admin & AI
| Screen | Key | File | Description |
|--------|-----|------|-------------|
| AI Analysis | `AI` | `AIScreen.jsx` | AI-powered farm analysis (Claude API) |
| Service Requests | `ServiceRequests` | `ServiceRequestsScreen.jsx` | Support ticket management |
| Activity Log | `ActivityLog` | `ActivityLogScreen.jsx` | Audit trail viewer |
| User Management | `Users` | `UsersScreen.jsx` | Create/manage users, set status |
| Role Management | `Roles` | `RolesScreen.jsx` | Edit role permissions, create custom roles |
| Settings | `Settings` | `SettingsScreen.jsx` | App and farm settings |

## State Management (Zustand — 5 stores)

| Store | File | Persistence | State |
|-------|------|------------|-------|
| `useAuthStore` | `useAuthStore.js` | AsyncStorage | Current user, JWT token, login/logout |
| `useFarmStore` | `useFarmStore.js` | AsyncStorage | Farm operations data, sensor simulation |
| `usePOSStore` | `usePOSStore.js` | AsyncStorage | Active POS session and cart |
| `useStoreStore` | `useStoreStore.js` | AsyncStorage | Store inventory and configuration |
| `useRolesStore` | `useRolesStore.js` | AsyncStorage | Role screen-access overrides, custom roles |

### useRolesStore — Dynamic RBAC

Admins can override which screens any role can access without changing code. Changes persist to the device and take effect immediately in the sidebar.

- `roleOverrides` — `{ [ROLE_NAME]: string[] }` admin-defined screen lists
- `customRoles` — array of fully custom roles with name, description, color, screens
- `canAccess(screenName, role)` — priority: custom roles → overrides → `permissions.js` defaults
- `screensForRole(roleName)` — full list of accessible screens for a given role
- Admin UI: **Role Management** screen (admin-only) with section-grouped screen toggles per role

## Role-Based Access Control

17 built-in roles. `permissions.js` defines the default `SCREEN_ACCESS` map. `useRolesStore` allows runtime overrides.

| Role | Color | Description |
|------|-------|-------------|
| ADMIN | Red | Full system access |
| MANAGER | Accent | All operational screens |
| SUPERVISOR | Blue | Operations + supply chain; no admin |
| WORKER | Green | Core farm ops screens |
| VIEWER | Grey | Dashboard + reports (read-only) |
| STORE_MANAGER | Orange | Store, POS, logistics, financials |
| CASHIER | Amber | POS and store view |
| PACKER | Brown | Packing, scanner, stock |
| DRIVER | Cyan | Logistics, scanner |
| SCANNER | Dim | Scanner only |
| AQUA_TECH | Blue (#0288D1) | Aquaculture, feed, water, QA, stock |
| GREENHOUSE_TECH | Dark Green | Greenhouse, vertical farm, nursery, QA |
| POULTRY_TECH | Amber (#F57F17) | Poultry, feed, water, QA |
| FIELD_WORKER | Olive | Nursery, automation, compliance, water |
| QA_OFFICER | Purple | QA, compliance, all stock screens |
| FINANCE_ADMIN | Teal | Financial, reports, market, store |
| DRONE_OPS | Navy | Drones, automation, QA, field ops |

## API Services

All API calls go through `src/services/api.js`. The base URL is configured via the `EXPO_PUBLIC_API_URL` environment variable (set in `.env` files) and defaults to `http://localhost:8000`. The JWT token is automatically attached to all requests from `useAuthStore`.

## Configuration Files

| File | Purpose |
|------|---------|
| `src/config/theme.js` | Colors, typography, spacing, radius constants |
| `src/config/navigation.js` | Screen registry (name, label, icon, color, section) |
| `src/config/permissions.js` | Default role → screen access map; `ROLE_META` export |
| `src/config/apiConfig.js` | API base URL resolution |
| `src/styles/common.js` | Shared modal, table, form, and layout styles |

## Running

```bash
# Install dependencies
npm install

# Start Expo development server
npx expo start

# Specific platforms
npx expo start --ios
npx expo start --android
npx expo start --web     # http://localhost:8081

# Run Jest tests
npm test
```

## Docker (Web Build)

The `Dockerfile` performs a multi-stage build:
1. **Build stage** — Node.js installs deps and exports the Expo web build
2. **Serve stage** — Nginx serves the static files with SPA routing support

```bash
# Build and run mobile web via Docker
docker compose up mobile
# Served at http://localhost:8083
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | 19.2.0 | UI framework |
| react-native | 0.83.2 | Mobile framework |
| expo | 55.0.6 | Development platform |
| zustand | 4.5.5 | State management |
| react-native-chart-kit | 6.12.0 | Charts and graphs |
| lucide-react-native | 0.439.0 | Icon library |
| @react-native-async-storage/async-storage | 2.2.0 | Persistent local storage |
| jest / jest-expo | 29.7.0 | Testing framework |
