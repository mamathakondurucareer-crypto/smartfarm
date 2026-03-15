/**
 * Thin fetch wrapper around the SmartFarm FastAPI backend.
 */
import { API_BASE } from "../config/apiConfig";

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
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
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
      genBarcode:(id, token)         => request("POST",   `/api/store/products/${id}/barcode`,     null,  token),
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

  // ─── Activity Log ─────────────────────────────────────────────
  activityLog: {
    list: (token, params = "") => request("GET", `/api/activity-logs${params}`, null, token),
    get:  (id, token)          => request("GET", `/api/activity-logs/${id}`,    null, token),
  },
};
