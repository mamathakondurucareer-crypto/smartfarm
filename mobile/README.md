# Mobile — SmartFarm OS

React Native + Expo app supporting iOS, Android, and Web. 24 screens covering all farm management domains.

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
│   ├── screens/                    # 24 JSX screen components
│   ├── components/                 # Reusable UI components
│   ├── store/                      # Zustand state stores
│   ├── services/                   # API client layer
│   ├── context/                    # React context providers
│   ├── config/                     # App configuration files
│   ├── hooks/                      # Custom React hooks
│   └── data/                       # Default/fallback state data
├── __tests__/                      # Jest test files
├── __mocks__/                      # Jest mocks for native modules
└── assets/                         # Images and static assets
```

## Screens (24)

### Farm Operations
| Screen | File | Description |
|--------|------|-------------|
| Dashboard | `Dashboard.jsx` | KPI overview, quick stats |
| Aquaculture | `Aquaculture.jsx` | Ponds, fish batches, water quality |
| Greenhouse | `Greenhouse.jsx` | Greenhouse crop management |
| Vertical Farm | `VerticalFarm.jsx` | Vertical farming units |
| Poultry | `Poultry.jsx` | Flocks, ducks, eggs, beehives |
| Water | `Water.jsx` | Water management |
| Energy | `Energy.jsx` | Energy monitoring |
| Automation | `Automation.jsx` | Automation rules and schedules |
| Nursery | `Nursery.jsx` | Nursery/seedling management |

### Stock & Supply Chain
| Screen | File | Description |
|--------|------|-------------|
| Stock Produced | `StockProduced.jsx` | Production batches |
| Stock Sales | `StockSales.jsx` | Sales and shipments |
| Packing | `Packing.jsx` | Packing order management |
| Scanner | `Scanner.jsx` | Barcode/QR scanning |

### Store & Retail
| Screen | File | Description |
|--------|------|-------------|
| Store | `Store.jsx` | Store configuration and stock |
| POS | `POS.jsx` | Point-of-sale transactions |
| Logistics | `Logistics.jsx` | Delivery routes and trips |

### Finance
| Screen | File | Description |
|--------|------|-------------|
| Market | `Market.jsx` | Market prices and orders |
| Financial | `Financial.jsx` | Revenue, expenses, salary |
| Reports | `Reports.jsx` | Report generation and export |

### Admin & AI
| Screen | File | Description |
|--------|------|-------------|
| AI | `AI.jsx` | AI-powered farm analysis |
| Service Requests | `ServiceRequests.jsx` | Support ticket management |
| Activity Log | `ActivityLog.jsx` | Audit trail viewer |
| Users | `Users.jsx` | User and role management |

## State Management (Zustand)

| Store | File | State |
|-------|------|-------|
| `useAuthStore` | `authStore.js` | Current user, token, login/logout |
| `useFarmStore` | `farmStore.js` | Farm operations data |
| `usePOSStore` | `posStore.js` | Active POS session and cart |
| `useStoreStore` | `storeStore.js` | Store inventory and config |

## API Services

All API calls go through `src/services/`. The base URL is configured in `src/config/api.js` and defaults to `http://localhost:8000`. JWT token is automatically attached to requests from `useAuthStore`.

## Configuration Files

| File | Purpose |
|------|---------|
| `src/config/api.js` | Base API URL |
| `src/config/theme.js` | Colors, typography, spacing |
| `src/config/navigation.js` | Screen navigation structure |
| `src/config/permissions.js` | Role-based screen access |

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
