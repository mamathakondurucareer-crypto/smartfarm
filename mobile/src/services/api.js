/**
 * Thin fetch wrapper around the SmartFarm FastAPI backend.
 */
import { API_BASE } from "../config/apiConfig";

// Global 401 handler — set once at app boot by useAuthStore
let _onUnauthorized = null;
export function setUnauthorizedHandler(fn) {
  _onUnauthorized = fn;
}

async function request(method, path, body, token, formEncoded = false) {
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let bodyStr;
  if (body) {
    if (formEncoded) {
      headers["Content-Type"] = "application/x-www-form-urlencoded";
      bodyStr = new URLSearchParams(body).toString();
    } else {
      headers["Content-Type"] = "application/json";
      bodyStr = JSON.stringify(body);
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: bodyStr,
    cache: "no-store",
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && _onUnauthorized) {
      _onUnauthorized();
    }
    throw new Error(data.detail || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  // ─── Auth ─────────────────────────────────────────────────────
  login:   (username, password) => request("POST", "/api/auth/login", { username, password }, null, true),
  me:      (token)              => request("GET",  "/api/auth/me",    null, token),
  roles:   (token)              => request("GET",  "/api/auth/roles", null, token),

  users: {
    list:      (token)                => request("GET",   "/api/auth/users",              null, token),
    create:    (data, token)          => request("POST",  "/api/auth/admin/users",        data, token),
    update:    (id, data, token)      => request("PUT",   `/api/auth/users/${id}`,        data, token),
    setStatus: (id, is_active, token) => request("PATCH", `/api/auth/users/${id}/status`, { is_active }, token),
  },

  // ─── Store Config & Products ──────────────────────────────────
  store: {
    getConfig:    (token)            => request("GET",    "/api/store/config",                     null,  token),
    updateConfig: (data, token)      => request("PUT",    "/api/store/config",                     data,  token),
    products: {
      list:     (token, params = "") => request("GET",    `/api/store/products${params}`,          null,  token),
      get:      (id, token)          => request("GET",    `/api/store/products/${id}`,             null,  token),
      create:   (data, token)        => request("POST",   "/api/store/products",                   data,  token),
      update:   (id, data, token)    => request("PUT",    `/api/store/products/${id}`,             data,  token),
      deactivate:(id, token)         => request("DELETE", `/api/store/products/${id}`,             null,  token),
      genBarcode:(id, token)         => request("POST",   `/api/store/products/${id}/barcode`,     { product_id: id, prefix: "SFN" },  token),
    },
    priceRules: {
      list:   (token)            => request("GET",    "/api/store/price-rules",          null, token),
      create: (data, token)      => request("POST",   "/api/store/price-rules",          data, token),
      delete: (id, token)        => request("DELETE", `/api/store/price-rules/${id}`,    null, token),
    },
  },

  // ─── Store Stock ──────────────────────────────────────────────
  stock: {
    list:    (token)            => request("GET",  "/api/store/stock",          null, token),
    get:     (productId, token) => request("GET",  `/api/store/stock/${productId}`, null, token),
    low:     (token)            => request("GET",  "/api/store/stock/low",      null, token),
    adjust:  (data, token)      => request("POST", "/api/store/stock/adjust",   data, token),
    receive: (data, token)      => request("POST", "/api/store/stock/receive",  data, token),
  },

  // ─── Supply Chain Transfers ───────────────────────────────────
  supplyChain: {
    list:    (token, params = "")  => request("GET",  `/api/supply-chain/transfers${params}`, null, token),
    get:     (id, token)           => request("GET",  `/api/supply-chain/transfers/${id}`,    null, token),
    create:  (data, token)         => request("POST", "/api/supply-chain/transfers",          data, token),
    receive: (id, data, token)     => request("PUT",  `/api/supply-chain/transfers/${id}/receive`, data, token),
    reject:  (id, data, token)     => request("PUT",  `/api/supply-chain/transfers/${id}/reject`,  data, token),
  },

  // ─── POS ──────────────────────────────────────────────────────
  pos: {
    openSession:   (data, token)   => request("POST", "/api/store/pos/sessions",             data, token),
    closeSession:  (id, data, token) => request("PUT", `/api/store/pos/sessions/${id}/close`, data, token),
    activeSession: (token)         => request("GET",  "/api/store/pos/sessions/active",       null, token),
    sessions:      (token)         => request("GET",  "/api/store/pos/sessions",              null, token),
    checkout:      (data, token)   => request("POST", "/api/store/pos/checkout",              data, token),
    transactions:  (token, params = "") => request("GET", `/api/store/pos/transactions${params}`, null, token),
    getTransaction:(id, token)     => request("GET",  `/api/store/pos/transactions/${id}`,    null, token),
    void:          (id, token)     => request("POST", `/api/store/pos/transactions/${id}/void`, null, token),
    lookup:        (barcode, token)=> request("GET",  `/api/store/pos/lookup/${barcode}`,     null, token),
  },

  // ─── Packing ──────────────────────────────────────────────────
  packing: {
    list:         (token, params = "") => request("GET",  `/api/packing/orders${params}`,            null, token),
    get:          (id, token)          => request("GET",  `/api/packing/orders/${id}`,               null, token),
    create:       (data, token)        => request("POST", "/api/packing/orders",                     data, token),
    update:       (id, data, token)    => request("PUT",  `/api/packing/orders/${id}`,               data, token),
    start:        (id, token)          => request("POST", `/api/packing/orders/${id}/start`,         null, token),
    packItem:     (orderId, itemId, data, token) => request("POST", `/api/packing/orders/${orderId}/items/${itemId}/pack`, data, token),
    complete:     (id, token)          => request("POST", `/api/packing/orders/${id}/complete`,      null, token),
    barcodes:     (token)              => request("GET",  "/api/packing/barcodes",                   null, token),
    genBarcode:   (data, token)        => request("POST", "/api/packing/barcodes/generate",          data, token),
    scanBarcode:  (barcode, token)     => request("GET",  `/api/packing/barcodes/scan/${barcode}`,   null, token),
  },

  // ─── Logistics ────────────────────────────────────────────────
  logistics: {
    routes: {
      list:   (token)          => request("GET",  "/api/logistics/routes",      null, token),
      create: (data, token)    => request("POST", "/api/logistics/routes",      data, token),
    },
    trips: {
      list:    (token, params = "") => request("GET",  `/api/logistics/trips${params}`,        null, token),
      active:  (token)              => request("GET",  "/api/logistics/trips/active",          null, token),
      get:     (id, token)          => request("GET",  `/api/logistics/trips/${id}`,           null, token),
      create:  (data, token)        => request("POST", "/api/logistics/trips",                 data, token),
      status:  (id, data, token)    => request("PUT",  `/api/logistics/trips/${id}/status`,    data, token),
      addOrder:(id, data, token)    => request("POST", `/api/logistics/trips/${id}/orders`,    data, token),
      deliver: (tripId, orderId, data, token) => request("PUT", `/api/logistics/trips/${tripId}/orders/${orderId}/deliver`, data, token),
    },
  },

  // ─── Service Requests ─────────────────────────────────────────
  serviceRequests: {
    list:    (token, params = "") => request("GET",  `/api/service-requests${params}`,        null, token),
    get:     (id, token)          => request("GET",  `/api/service-requests/${id}`,           null, token),
    create:  (data, token)        => request("POST", "/api/service-requests",                 data, token),
    update:  (id, data, token)    => request("PUT",  `/api/service-requests/${id}`,           data, token),
    assign:  (id, data, token)    => request("PUT",  `/api/service-requests/${id}/assign`,    data, token),
    resolve: (id, data, token)    => request("PUT",  `/api/service-requests/${id}/resolve`,   data, token),
  },

  // ─── Reports ──────────────────────────────────────────────────
  reports: {
    sales:        (token, params = "") => request("GET", `/api/reports/sales${params}`,            null, token),
    production:   (token, params = "") => request("GET", `/api/reports/production${params}`,       null, token),
    financial:    (token)              => request("GET", "/api/reports/financial-summary",         null, token),
    storeDaily:   (token)              => request("GET", "/api/reports/store-daily",               null, token),
    stockMovement:(token, params = "") => request("GET", `/api/reports/stock-movement${params}`,   null, token),
    inventory:    (token)              => request("GET", "/api/reports/inventory-valuation",       null, token),
  },

  // ─── Sensors & IoT ───────────────────────────────────────────
  sensors: {
    devices:      (token, params = "")  => request("GET",  `/api/sensors/devices${params}`,          null, token),
    bulkIngest:   (token, readings)     => request("POST", "/api/sensors/readings/bulk",              { readings }, token),
    latestAll:    (token)               => request("GET",  "/api/sensors/latest-all",                 null, token),
    latestByZone: (zone, token)         => request("GET",  `/api/sensors/latest-by-zone/${zone}`,     null, token),
    waterSummary: (token)               => request("GET",  "/api/sensors/water-summary",              null, token),
    energySummary:(token)               => request("GET",  "/api/sensors/energy-summary",             null, token),
    alerts:       (token, params = "")  => request("GET",  `/api/sensors/alerts${params}`,            null, token),
    ackAlert:     (id, token)           => request("PUT",  `/api/sensors/alerts/${id}/acknowledge`,   null, token),
    resolveAlert: (id, token)           => request("PUT",  `/api/sensors/alerts/${id}/resolve`,       null, token),
  },

  // ─── Automation ───────────────────────────────────────────────
  automation: {
    status:     (token)           => request("GET", "/api/automation/status",             null, token),
    rules:      (token)           => request("GET", "/api/automation/rules",              null, token),
    toggleRule: (id, token)       => request("PUT", `/api/automation/rules/${id}/toggle`, null, token),
    logs:       (token, params="")=> request("GET", `/api/automation/logs${params}`,      null, token),
  },

  // ─── Aquaculture ──────────────────────────────────────────────
  aquaculture: {
    ponds:      (token, params = "") => request("GET", `/api/aquaculture/ponds${params}`, null, token),
    summary:    (token)              => request("GET", "/api/aquaculture/summary",         null, token),
    batches:    (token)              => request("GET", "/api/aquaculture/batches",          null, token),
  },

  // ─── Crops (Greenhouse / Vertical Farm) ───────────────────────
  crops: {
    greenhouse:  (token)           => request("GET",  "/api/crops/greenhouse",    null, token),
    verticalFarm:(token)           => request("GET",  "/api/crops/vertical-farm", null, token),
  },

  // ─── Poultry ──────────────────────────────────────────────────
  poultry: {
    flocks: (token) => request("GET", "/api/poultry/flocks", null, token),
    ducks:  (token) => request("GET", "/api/poultry/ducks",  null, token),
    bees:   (token) => request("GET", "/api/poultry/bees",   null, token),
  },

  // ─── Dashboard ────────────────────────────────────────────────
  dashboard: {
    kpis:             (token, params = "") => request("GET", `/api/dashboard/kpis${params}`,              null, token),
    revenueByStream:  (token, params = "") => request("GET", `/api/dashboard/revenue-by-stream${params}`,  null, token),
    monthlyPnl:       (token, params = "") => request("GET", `/api/dashboard/monthly-pnl${params}`,        null, token),
  },

  // ─── Activity Log ─────────────────────────────────────────────
  activityLog: {
    list: (token, params = "") => request("GET", `/api/activity-logs${params}`, null, token),
    get:  (id, token)          => request("GET", `/api/activity-logs/${id}`,    null, token),
  },

  // ─── Feed Production ──────────────────────────────────────────
  feedProduction: {
    bsf: {
      list:   (token)            => request("GET",    "/api/feed-production/bsf",       null, token),
      create: (data, token)      => request("POST",   "/api/feed-production/bsf",       data, token),
      update: (id, data, token)  => request("PUT",    `/api/feed-production/bsf/${id}`, data, token),
      delete: (id, token)        => request("DELETE", `/api/feed-production/bsf/${id}`, null, token),
    },
    azolla: {
      list:   (token)       => request("GET",  "/api/feed-production/azolla", null, token),
      create: (data, token) => request("POST", "/api/feed-production/azolla", data, token),
    },
    duckweed: {
      list:   (token)       => request("GET",  "/api/feed-production/duckweed", null, token),
      create: (data, token) => request("POST", "/api/feed-production/duckweed", data, token),
    },
    batches: {
      list:   (token)       => request("GET",    "/api/feed-production/batches",       null, token),
      create: (data, token) => request("POST",   "/api/feed-production/batches",       data, token),
      delete: (id, token)   => request("DELETE", `/api/feed-production/batches/${id}`, null, token),
    },
    inventory: {
      list:   (token)       => request("GET",    "/api/feed-production/inventory",       null, token),
      create: (data, token) => request("POST",   "/api/feed-production/inventory",       data, token),
      delete: (id, token)   => request("DELETE", `/api/feed-production/inventory/${id}`, null, token),
    },
    selfSufficiency: (token) => request("GET", "/api/feed-production/self-sufficiency", null, token),
  },

  // ─── Drones ───────────────────────────────────────────────────
  drones: {
    list:   (token)           => request("GET",    "/api/drones",       null, token),
    create: (data, token)     => request("POST",   "/api/drones",       data, token),
    update: (id, data, token) => request("PUT",    `/api/drones/${id}`, data, token),
    delete: (id, token)       => request("DELETE", `/api/drones/${id}`, null, token),
    flights: {
      list:   (token)       => request("GET",    "/api/drones/flights",       null, token),
      create: (data, token) => request("POST",   "/api/drones/flights",       data, token),
      delete: (id, token)   => request("DELETE", `/api/drones/flights/${id}`, null, token),
    },
    sprays: {
      list:   (token)       => request("GET",  "/api/drones/sprays", null, token),
      create: (data, token) => request("POST", "/api/drones/sprays", data, token),
    },
  },

  // ─── QA & Traceability ────────────────────────────────────────
  qa: {
    lots: {
      list:         (token)                => request("GET",   "/api/qa/lots",                      null,  token),
      create:       (data, token)          => request("POST",  "/api/qa/lots",                      data,  token),
      get:          (id, token)            => request("GET",   `/api/qa/lots/${id}`,                null,  token),
      trace:        (lotCode, token)       => request("GET",   `/api/qa/lots/trace/${lotCode}`,     null,  token),
      updateStatus: (id, status, token)    => request("PATCH", `/api/qa/lots/${id}/status?status=${status}`, null, token),
    },
    tests: {
      list:   (token)       => request("GET",  "/api/qa/tests", null, token),
      create: (data, token) => request("POST", "/api/qa/tests", data, token),
    },
    quarantine: {
      list:    (token)            => request("GET",  "/api/qa/quarantine",               null, token),
      create:  (data, token)      => request("POST", "/api/qa/quarantine",               data, token),
      resolve: (id, data, token)  => request("PUT",  `/api/qa/quarantine/${id}/resolve`, data, token),
    },
  },

  // ─── Compliance & Licences ────────────────────────────────────
  compliance: {
    licences: {
      list:         (token)           => request("GET",    "/api/compliance/licences",               null, token),
      create:       (data, token)     => request("POST",   "/api/compliance/licences",               data, token),
      update:       (id, data, token) => request("PUT",    `/api/compliance/licences/${id}`,         data, token),
      delete:       (id, token)       => request("DELETE", `/api/compliance/licences/${id}`,         null, token),
      expiringSoon: (token)           => request("GET",    "/api/compliance/licences/expiring-soon", null, token),
    },
    tasks: {
      list:   (token)           => request("GET",    "/api/compliance/tasks",       null, token),
      create: (data, token)     => request("POST",   "/api/compliance/tasks",       data, token),
      update: (id, data, token) => request("PUT",    `/api/compliance/tasks/${id}`, data, token),
      delete: (id, token)       => request("DELETE", `/api/compliance/tasks/${id}`, null, token),
    },
  },

  // ─── Market Prices ────────────────────────────────────────────
  market: {
    latestPrices: (token) => request("GET", "/api/market/prices/latest", null, token),
    prices:       (token, params = "") => request("GET", `/api/market/prices${params}`, null, token),
    recordPrice:  (data, token) => request("POST", "/api/market/prices", data, token),
    orders:       (token, params = "") => request("GET", `/api/market/orders${params}`, null, token),
    shipments:    (token, params = "") => request("GET", `/api/market/shipments${params}`, null, token),
  },

  // ─── Nursery (Backend) ────────────────────────────────────────
  nursery: {
    batches: {
      list:    (token)           => request("GET",    "/api/nursery/batches",          null, token),
      create:  (data, token)     => request("POST",   "/api/nursery/batches",          data, token),
      update:  (id, data, token) => request("PUT",    `/api/nursery/batches/${id}`,    data, token),
      delete:  (id, token)       => request("DELETE", `/api/nursery/batches/${id}`,    null, token),
      summary: (token)           => request("GET",    "/api/nursery/batches/summary",  null, token),
    },
    orders: {
      list:   (token)           => request("GET",    "/api/nursery/orders",       null, token),
      create: (data, token)     => request("POST",   "/api/nursery/orders",       data, token),
      update: (id, data, token) => request("PUT",    `/api/nursery/orders/${id}`, data, token),
      delete: (id, token)       => request("DELETE", `/api/nursery/orders/${id}`, null, token),
    },
  },
};
