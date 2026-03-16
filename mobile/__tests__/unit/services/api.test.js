/**
 * Unit tests for the API service layer.
 */

// Mock global fetch
global.fetch = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
});

// Helper to create a mock fetch response
function mockFetchOk(body) {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(body),
  });
}

function mockFetchError(status, detail) {
  return Promise.resolve({
    ok: false,
    status,
    json: () => Promise.resolve({ detail }),
  });
}

// We import after setting up the mock
// Note: the api module uses API_BASE from apiConfig. Mock that too.
jest.mock("../../../src/config/apiConfig", () => ({
  API_BASE: "http://test.api",
}));

const { api } = require("../../../src/services/api");

// ── api.login ───────────────────────────────────────────────────────────────
describe("api.login", () => {
  it("sends POST to /api/auth/login with form encoding", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ access_token: "token123", token_type: "bearer", username: "admin", role: "admin" })
    );

    await api.login("admin", "admin123");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/auth/login",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/x-www-form-urlencoded",
        }),
      })
    );
  });

  it("returns token data on success", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ access_token: "jwt.token", token_type: "bearer", username: "admin", role: "admin" })
    );

    const result = await api.login("admin", "admin123");

    expect(result.access_token).toBe("jwt.token");
    expect(result.username).toBe("admin");
  });

  it("throws error on 401", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchError(401, "Invalid credentials")
    );

    await expect(api.login("admin", "wrong")).rejects.toThrow("Invalid credentials");
  });
});

// ── api.me ──────────────────────────────────────────────────────────────────
describe("api.me", () => {
  it("sends GET to /api/auth/me with bearer token", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ id: 1, username: "admin", role_id: 1 })
    );

    await api.me("test-token");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/auth/me",
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      })
    );
  });

  it("returns user data on success", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ id: 1, username: "admin", email: "admin@smartfarm.in" })
    );

    const user = await api.me("token");
    expect(user.id).toBe(1);
    expect(user.username).toBe("admin");
  });

  it("throws on 401", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchError(401, "Not authenticated")
    );

    await expect(api.me("invalid-token")).rejects.toThrow("Not authenticated");
  });
});

// ── api.store.products.list ──────────────────────────────────────────────────
describe("api.store.products.list", () => {
  it("sends GET to /api/store/products", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk([{ id: 1, name: "Murrel Fish" }])
    );

    await api.store.products.list("token");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/store/products",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("appends query params when provided", async () => {
    global.fetch.mockImplementationOnce(() => mockFetchOk([]));

    await api.store.products.list("token", "?category=fish");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/store/products?category=fish",
      expect.anything()
    );
  });
});

// ── api.pos.checkout ────────────────────────────────────────────────────────
describe("api.pos.checkout", () => {
  it("sends POST to /api/store/pos/checkout with JSON body", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ id: 1, transaction_code: "TXN-001", total_amount: 367.5, status: "completed", items: [] })
    );

    const payload = {
      session_id: 1,
      items: [{ product_id: 1, quantity: 1, discount_pct: 0 }],
      payment_mode: "cash",
      amount_tendered: 400,
    };

    await api.pos.checkout(payload, "token");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/store/pos/checkout",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify(payload),
      })
    );
  });

  it("returns transaction data on success", async () => {
    const mockTxn = {
      id: 1,
      transaction_code: "TXN-001",
      total_amount: 367.5,
      status: "completed",
      items: [{ id: 1, product_name: "Murrel Fish", quantity: 1 }],
    };
    global.fetch.mockImplementationOnce(() => mockFetchOk(mockTxn));

    const result = await api.pos.checkout({ session_id: 1, items: [] }, "token");

    expect(result.transaction_code).toBe("TXN-001");
    expect(result.items).toHaveLength(1);
  });
});

// ── api.pos.lookup ──────────────────────────────────────────────────────────
describe("api.pos.lookup", () => {
  it("sends GET to /api/store/pos/lookup/:barcode", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ found: true, result: { type: "product", product_id: 1, name: "Murrel Fish" } })
    );

    await api.pos.lookup("SFN0001ABC", "token");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/store/pos/lookup/SFN0001ABC",
      expect.anything()
    );
  });

  it("returns found:false for unknown barcode", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ found: false })
    );

    const result = await api.pos.lookup("UNKNOWN", "token");
    expect(result.found).toBe(false);
  });
});

// ── api.reports.sales ───────────────────────────────────────────────────────
describe("api.reports.sales", () => {
  it("sends GET to /api/reports/sales", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ total_revenue: 5000, total_transactions: 10 })
    );

    await api.reports.sales("token");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/reports/sales",
      expect.objectContaining({ method: "GET" })
    );
  });

  it("appends date range params", async () => {
    global.fetch.mockImplementationOnce(() => mockFetchOk({}));

    await api.reports.sales("token", "?start_date=2025-01-01&end_date=2025-12-31");

    expect(fetch).toHaveBeenCalledWith(
      "http://test.api/api/reports/sales?start_date=2025-01-01&end_date=2025-12-31",
      expect.anything()
    );
  });
});

// ── Error handling edge cases ────────────────────────────────────────────────
describe("error handling", () => {
  it("throws with detail message from server error response", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchError(422, "Validation error: quantity must be positive")
    );

    await expect(
      api.store.products.create({ name: "" }, "token")
    ).rejects.toThrow("Validation error: quantity must be positive");
  });

  it("throws generic message when server returns no detail", async () => {
    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error("parse error")),
      })
    );

    await expect(api.me("token")).rejects.toThrow("Request failed (500)");
  });

  it("propagates network errors", async () => {
    global.fetch.mockImplementationOnce(() =>
      Promise.reject(new Error("Network error"))
    );

    await expect(api.me("token")).rejects.toThrow("Network error");
  });
});

// ── api.store.products.genBarcode sends body ─────────────────────────────────
describe("api.store.products.genBarcode", () => {
  it("sends POST with product_id and prefix in body", async () => {
    global.fetch.mockImplementationOnce(() =>
      mockFetchOk({ barcode: "SFN0001ABC123ABCD" })
    );

    await api.store.products.genBarcode(1, "token");

    const call = fetch.mock.calls[0];
    const body = JSON.parse(call[1].body);
    expect(body.product_id).toBe(1);
    expect(body.prefix).toBe("SFN");
  });
});
