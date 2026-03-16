"""Functional tests for Packing Orders and Barcode Registry endpoints."""

import pytest


# ═══════════════════════════════════════════════════════════════
# PACKING ORDERS
# ═══════════════════════════════════════════════════════════════
class TestPackingOrders:
    def test_list_packing_orders(self, client, admin_headers):
        resp = client.get("/api/packing/orders", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        orders = data if isinstance(data, list) else data.get("orders", [])
        assert isinstance(orders, list)

    def test_list_orders_unauthenticated(self, client):
        resp = client.get("/api/packing/orders")
        assert resp.status_code == 401

    def test_create_packing_order(self, client, admin_headers, test_product):
        resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "notes": "Test packing order",
                "items": [
                    {
                        "product_id": test_product["id"],
                        "quantity_required": 10.0,
                    }
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "packing_order_code" in data
        assert data["status"] == "pending"
        assert len(data.get("items", [])) == 1
        assert data["items"][0]["product_id"] == test_product["id"]

    def test_create_packing_order_multiple_items(self, client, admin_headers, test_products):
        resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "notes": "Multi-item packing order",
                "items": [
                    {"product_id": test_products[0]["id"], "quantity_required": 5.0},
                    {"product_id": test_products[1]["id"], "quantity_required": 8.0},
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data.get("items", [])) == 2

    def test_create_order_empty_items_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [],
            },
        )
        assert resp.status_code in (400, 422)

    def test_create_order_invalid_product_rejected(self, client, admin_headers):
        resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [{"product_id": 99999, "quantity_required": 5.0}],
            },
        )
        assert resp.status_code in (400, 404, 422)

    def test_create_order_viewer_forbidden(self, client, viewer_headers, test_product):
        resp = client.post(
            "/api/packing/orders",
            headers=viewer_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [{"product_id": test_product["id"], "quantity_required": 2.0}],
            },
        )
        assert resp.status_code == 403

    def test_get_packing_order_by_id(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [{"product_id": test_product["id"], "quantity_required": 3.0}],
            },
        )
        assert create_resp.status_code == 201
        order_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/packing/orders/{order_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == order_id

    def test_get_order_not_found(self, client, admin_headers):
        resp = client.get("/api/packing/orders/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_start_packing_order(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [{"product_id": test_product["id"], "quantity_required": 4.0}],
            },
        )
        assert create_resp.status_code == 201
        order_id = create_resp.json()["id"]

        start_resp = client.post(
            f"/api/packing/orders/{order_id}/start",
            headers=admin_headers,
        )
        assert start_resp.status_code in (200, 201)
        data = start_resp.json()
        assert data["order_id"] == order_id

    def test_pack_item(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [{"product_id": test_product["id"], "quantity_required": 5.0}],
            },
        )
        assert create_resp.status_code == 201
        order = create_resp.json()
        order_id = order["id"]
        item_id = order["items"][0]["id"]

        # Start order first
        client.post(f"/api/packing/orders/{order_id}/start", headers=admin_headers)

        # Pack the item
        pack_resp = client.post(
            f"/api/packing/orders/{order_id}/items/{item_id}/pack",
            headers=admin_headers,
            json={"quantity_packed": 5.0, "batch_notes": "Test pack"},
        )
        assert pack_resp.status_code in (200, 201)
        data = pack_resp.json()
        assert data["quantity_packed"] == 5.0

    def test_complete_packing_order(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/packing/orders",
            headers=admin_headers,
            json={
                "order_ref_type": "store_replenishment",
                "items": [{"product_id": test_product["id"], "quantity_required": 2.0}],
            },
        )
        assert create_resp.status_code == 201
        order = create_resp.json()
        order_id = order["id"]
        item_id = order["items"][0]["id"]

        # Start → pack → complete
        client.post(f"/api/packing/orders/{order_id}/start", headers=admin_headers)
        client.post(
            f"/api/packing/orders/{order_id}/items/{item_id}/pack",
            headers=admin_headers,
            json={"quantity_packed": 2.0},
        )
        complete_resp = client.post(
            f"/api/packing/orders/{order_id}/complete",
            headers=admin_headers,
        )
        assert complete_resp.status_code in (200, 201)
        data = complete_resp.json()
        assert data["order_id"] == order_id

    def test_filter_orders_by_status(self, client, admin_headers):
        resp = client.get("/api/packing/orders?status=pending", headers=admin_headers)
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════
# BARCODE REGISTRY
# ═══════════════════════════════════════════════════════════════
class TestBarcodeRegistry:
    def test_list_barcodes(self, client, admin_headers):
        resp = client.get("/api/packing/barcodes", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_generate_barcode(self, client, admin_headers, test_product):
        resp = client.post(
            "/api/packing/barcodes/generate",
            headers=admin_headers,
            json={
                "product_id": test_product["id"],
                "entity_type": "packing_order",
                "entity_id": 1,
                "prefix": "PKG",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "barcode" in data

    def test_scan_barcode_not_found(self, client, admin_headers):
        resp = client.get(
            "/api/packing/barcodes/scan/INVALID-BARCODE-XYZ",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("found") is False

    def test_scan_requires_auth(self, client):
        resp = client.get("/api/packing/barcodes/scan/SOMEBARCODE")
        assert resp.status_code == 401

    def test_generate_and_scan_barcode(self, client, admin_headers, test_product):
        gen_resp = client.post(
            "/api/packing/barcodes/generate",
            headers=admin_headers,
            json={
                "product_id": test_product["id"],
                "entity_type": "product",
                "entity_id": test_product["id"],
                "prefix": "SFN",
            },
        )
        assert gen_resp.status_code in (200, 201)
        barcode = gen_resp.json().get("barcode", "")

        if barcode:
            scan_resp = client.get(
                f"/api/packing/barcodes/scan/{barcode}",
                headers=admin_headers,
            )
            assert scan_resp.status_code == 200
            data = scan_resp.json()
            assert data.get("found") is True
            assert data.get("result") is not None
