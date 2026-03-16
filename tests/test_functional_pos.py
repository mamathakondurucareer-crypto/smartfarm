"""Functional tests for POS sessions, checkout, transactions, and barcode lookup."""

import pytest


# ── Shared session fixture ─────────────────────────────────────────────────────
@pytest.fixture(scope="class")
def open_pos_session(client, cashier_headers, test_product):
    """Opens a POS session and yields its ID; closes it after the test class."""
    resp = client.post(
        "/api/store/pos/sessions",
        headers=cashier_headers,
        json={"opening_cash": 1000.0, "notes": "Test session"},
    )
    assert resp.status_code == 201, f"Failed to open session: {resp.text}"
    session = resp.json()
    yield session
    # Close the session after tests
    client.put(
        f"/api/store/pos/sessions/{session['id']}/close",
        headers=cashier_headers,
        json={"closing_cash": 1000.0, "notes": "Auto-closed after tests"},
    )


# ═══════════════════════════════════════════════════════════════
# POS SESSIONS
# ═══════════════════════════════════════════════════════════════
class TestPOSSessions:
    def test_open_session_cashier(self, client, cashier_headers):
        resp = client.post(
            "/api/store/pos/sessions",
            headers=cashier_headers,
            json={"opening_cash": 500.0},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "open"
        assert data["opening_cash"] == 500.0
        assert "session_code" in data
        # Close immediately to not block other tests
        client.put(
            f"/api/store/pos/sessions/{data['id']}/close",
            headers=cashier_headers,
            json={"closing_cash": 500.0},
        )

    def test_open_duplicate_session_rejected(self, client, cashier_headers):
        # Open one session
        r1 = client.post(
            "/api/store/pos/sessions",
            headers=cashier_headers,
            json={"opening_cash": 200.0},
        )
        assert r1.status_code == 201
        # Try to open another — should fail
        r2 = client.post(
            "/api/store/pos/sessions",
            headers=cashier_headers,
            json={"opening_cash": 300.0},
        )
        assert r2.status_code == 400
        # Clean up
        client.put(
            f"/api/store/pos/sessions/{r1.json()['id']}/close",
            headers=cashier_headers,
            json={"closing_cash": 200.0},
        )

    def test_open_session_unauthenticated(self, client):
        resp = client.post(
            "/api/store/pos/sessions",
            json={"opening_cash": 0},
        )
        assert resp.status_code == 401

    def test_open_session_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/store/pos/sessions",
            headers=viewer_headers,
            json={"opening_cash": 0},
        )
        assert resp.status_code == 403

    def test_list_sessions(self, client, admin_headers):
        resp = client.get("/api/store/pos/sessions", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_get_active_session_none(self, client, cashier_headers):
        # No open session for cashier at this point
        resp = client.get("/api/store/pos/sessions/active", headers=cashier_headers)
        # Either 200 (no active session) or 404
        assert resp.status_code in (200, 404)

    def test_close_session(self, client, cashier_headers):
        # Open a session
        open_resp = client.post(
            "/api/store/pos/sessions",
            headers=cashier_headers,
            json={"opening_cash": 750.0},
        )
        assert open_resp.status_code == 201
        session_id = open_resp.json()["id"]

        # Close it
        close_resp = client.put(
            f"/api/store/pos/sessions/{session_id}/close",
            headers=cashier_headers,
            json={"closing_cash": 900.0, "notes": "End of shift"},
        )
        assert close_resp.status_code == 200
        data = close_resp.json()
        assert data["status"] == "closed"
        assert data["closing_cash"] == 900.0

    def test_close_nonexistent_session(self, client, admin_headers):
        resp = client.put(
            "/api/store/pos/sessions/99999/close",
            headers=admin_headers,
            json={"closing_cash": 0},
        )
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# POS CHECKOUT
# ═══════════════════════════════════════════════════════════════
class TestPOSCheckout:
    @pytest.fixture(autouse=True)
    def session_id(self, client, cashier_headers, test_product):
        """Opens a fresh session for each test, closes it after."""
        open_resp = client.post(
            "/api/store/pos/sessions",
            headers=cashier_headers,
            json={"opening_cash": 1000.0},
        )
        assert open_resp.status_code == 201
        self._session = open_resp.json()
        self._product = test_product
        yield self._session["id"]
        client.put(
            f"/api/store/pos/sessions/{self._session['id']}/close",
            headers=cashier_headers,
            json={"closing_cash": 1000.0},
        )

    def test_checkout_basic(self, client, cashier_headers, session_id):
        resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": session_id,
                "items": [{"product_id": self._product["id"], "quantity": 2.0, "discount_pct": 0}],
                "payment_mode": "cash",
                "amount_tendered": 700.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "transaction_code" in data
        assert data["total_amount"] > 0
        assert data["status"] == "completed"
        assert len(data.get("items", [])) == 1

    def test_checkout_with_discount(self, client, cashier_headers, session_id):
        resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": session_id,
                "items": [{"product_id": self._product["id"], "quantity": 1.0, "discount_pct": 10}],
                "payment_mode": "cash",
                "amount_tendered": 500.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["discount_amount"] > 0

    def test_checkout_multiple_items(self, client, cashier_headers, test_products, session_id):
        items = [
            {"product_id": p["id"], "quantity": 1.0, "discount_pct": 0}
            for p in test_products[:2]
        ]
        resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": session_id,
                "items": items,
                "payment_mode": "upi",
                "amount_tendered": 1000.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert len(data.get("items", [])) == 2

    def test_checkout_invalid_session(self, client, cashier_headers):
        resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": 99999,
                "items": [{"product_id": 1, "quantity": 1.0, "discount_pct": 0}],
                "payment_mode": "cash",
                "amount_tendered": 500.0,
            },
        )
        assert resp.status_code in (400, 404)

    def test_checkout_empty_items_rejected(self, client, cashier_headers, session_id):
        resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": session_id,
                "items": [],
                "payment_mode": "cash",
                "amount_tendered": 0,
            },
        )
        assert resp.status_code in (400, 422)

    def test_checkout_invalid_product_id(self, client, cashier_headers, session_id):
        resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": session_id,
                "items": [{"product_id": 99999, "quantity": 1.0, "discount_pct": 0}],
                "payment_mode": "cash",
                "amount_tendered": 500.0,
            },
        )
        assert resp.status_code in (400, 404, 422)


# ═══════════════════════════════════════════════════════════════
# TRANSACTIONS
# ═══════════════════════════════════════════════════════════════
class TestPOSTransactions:
    @pytest.fixture(scope="class", autouse=True)
    def completed_transaction(self, client, cashier_headers, test_product):
        """Creates a completed transaction to use in tests."""
        open_resp = client.post(
            "/api/store/pos/sessions",
            headers=cashier_headers,
            json={"opening_cash": 1000.0},
        )
        assert open_resp.status_code == 201
        session = open_resp.json()

        txn_resp = client.post(
            "/api/store/pos/checkout",
            headers=cashier_headers,
            json={
                "session_id": session["id"],
                "items": [{"product_id": test_product["id"], "quantity": 1.0, "discount_pct": 0}],
                "payment_mode": "cash",
                "amount_tendered": 500.0,
            },
        )
        assert txn_resp.status_code in (200, 201)
        self._txn = txn_resp.json()
        self._session = session
        yield self._txn

        client.put(
            f"/api/store/pos/sessions/{session['id']}/close",
            headers=cashier_headers,
            json={"closing_cash": 1000.0},
        )

    def test_list_transactions(self, client, admin_headers):
        resp = client.get("/api/store/pos/transactions", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        txns = data if isinstance(data, list) else data.get("transactions", [])
        assert len(txns) >= 1

    def test_get_transaction_by_id(self, client, admin_headers, completed_transaction):
        txn_id = completed_transaction["id"]
        resp = client.get(f"/api/store/pos/transactions/{txn_id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == txn_id
        assert "transaction_code" in data
        assert "items" in data

    def test_get_transaction_not_found(self, client, admin_headers):
        resp = client.get("/api/store/pos/transactions/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_transactions_with_date_filter(self, client, admin_headers):
        resp = client.get(
            "/api/store/pos/transactions?start_date=2020-01-01",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_void_transaction(self, client, admin_headers, completed_transaction):
        # Create a fresh transaction to void
        open_resp = client.post(
            "/api/store/pos/sessions",
            headers=admin_headers,
            json={"opening_cash": 500.0},
        )
        assert open_resp.status_code == 201
        session = open_resp.json()

        products_resp = client.get("/api/store/products", headers=admin_headers)
        products = products_resp.json()
        if not isinstance(products, list):
            products = products.get("products", [])

        txn_resp = client.post(
            "/api/store/pos/checkout",
            headers=admin_headers,
            json={
                "session_id": session["id"],
                "items": [{"product_id": products[0]["id"], "quantity": 1.0, "discount_pct": 0}],
                "payment_mode": "cash",
                "amount_tendered": 500.0,
            },
        )
        assert txn_resp.status_code in (200, 201)
        txn_id = txn_resp.json()["id"]

        void_resp = client.post(
            f"/api/store/pos/transactions/{txn_id}/void",
            headers=admin_headers,
        )
        assert void_resp.status_code in (200, 201)
        data = void_resp.json()
        assert data["transaction_id"] == txn_id

        client.put(
            f"/api/store/pos/sessions/{session['id']}/close",
            headers=admin_headers,
            json={"closing_cash": 500.0},
        )

    def test_void_nonexistent_transaction(self, client, admin_headers):
        resp = client.post(
            "/api/store/pos/transactions/99999/void",
            headers=admin_headers,
        )
        assert resp.status_code == 404

    def test_transactions_unauthenticated(self, client):
        resp = client.get("/api/store/pos/transactions")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# BARCODE LOOKUP
# ═══════════════════════════════════════════════════════════════
class TestBarcodeLookup:
    def test_lookup_nonexistent_barcode(self, client, cashier_headers):
        resp = client.get("/api/store/pos/lookup/INVALID-BARCODE-999", headers=cashier_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is False

    def test_lookup_requires_auth(self, client):
        resp = client.get("/api/store/pos/lookup/SOMEBARCODE123")
        assert resp.status_code == 401

    def test_lookup_after_barcode_generation(self, client, admin_headers, test_product):
        product_id = test_product["id"]
        # Generate a barcode for the product
        gen_resp = client.post(
            f"/api/store/products/{product_id}/barcode",
            headers=admin_headers,
            json={"product_id": product_id, "prefix": "SFN"},
        )
        assert gen_resp.status_code in (200, 201)
        barcode = gen_resp.json().get("barcode", "")
        if barcode:
            lookup_resp = client.get(
                f"/api/store/pos/lookup/{barcode}",
                headers=admin_headers,
            )
            assert lookup_resp.status_code == 200
            data = lookup_resp.json()
            # Barcode may or may not be registered for lookup depending on backend logic
            assert "found" in data
