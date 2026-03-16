"""Functional tests for Store Config, Product Catalog, Price Rules, and Stock endpoints."""

import pytest


# ═══════════════════════════════════════════════════════════════
# STORE CONFIG
# ═══════════════════════════════════════════════════════════════
class TestStoreConfig:
    def test_get_config_authenticated(self, client, admin_headers):
        resp = client.get("/api/store/config", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "store_name" in data
        assert "currency" in data

    def test_get_config_unauthenticated(self, client):
        resp = client.get("/api/store/config")
        assert resp.status_code == 401

    def test_update_config(self, client, admin_headers):
        resp = client.put(
            "/api/store/config",
            headers=admin_headers,
            json={"store_name": "Updated Test Store", "currency": "INR"},
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["store_name"] == "Updated Test Store"

    def test_update_config_viewer_forbidden(self, client, viewer_headers):
        resp = client.put(
            "/api/store/config",
            headers=viewer_headers,
            json={"store_name": "Viewer Update Attempt"},
        )
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════
# PRODUCT CATALOG
# ═══════════════════════════════════════════════════════════════
class TestProductCatalog:
    def test_list_products(self, client, admin_headers):
        resp = client.get("/api/store/products", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        products = data if isinstance(data, list) else data.get("products", [])
        assert len(products) >= 2  # seeded in conftest

    def test_list_products_unauthenticated(self, client):
        resp = client.get("/api/store/products")
        assert resp.status_code == 401

    def test_get_product_by_id(self, client, admin_headers, test_product):
        product_id = test_product["id"]
        resp = client.get(f"/api/store/products/{product_id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == product_id
        assert "name" in data
        assert "selling_price" in data

    def test_get_product_not_found(self, client, admin_headers):
        resp = client.get("/api/store/products/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_create_product(self, client, admin_headers):
        resp = client.post(
            "/api/store/products",
            headers=admin_headers,
            json={
                "product_code": "TEST-NEW-01",
                "name": "New Test Vegetable",
                "category": "vegetables",
                "source_type": "farm_produced",
                "unit": "kg",
                "selling_price": 60.0,
                "mrp": 70.0,
                "cost_price": 30.0,
                "gst_rate": 0.0,
                "is_weighable": True,
                "track_expiry": False,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "New Test Vegetable"
        assert data["selling_price"] == 60.0

    def test_create_product_duplicate_code(self, client, admin_headers):
        payload = {
            "product_code": "TEST-DUP-01",
            "name": "Dup Product",
            "category": "vegetables",
            "source_type": "farm_produced",
            "unit": "kg",
            "selling_price": 50.0,
            "mrp": 60.0,
            "cost_price": 25.0,
            "gst_rate": 0.0,
            "is_weighable": True,
            "track_expiry": False,
        }
        client.post("/api/store/products", headers=admin_headers, json=payload)
        resp = client.post("/api/store/products", headers=admin_headers, json=payload)
        assert resp.status_code == 400

    def test_create_product_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/store/products",
            headers=viewer_headers,
            json={
                "product_code": "TEST-VW-01",
                "name": "Viewer Product",
                "category": "vegetables",
                "source_type": "farm_produced",
                "unit": "kg",
                "selling_price": 50.0,
                "mrp": 60.0,
                "cost_price": 25.0,
                "gst_rate": 0.0,
                "is_weighable": True,
                "track_expiry": False,
            },
        )
        assert resp.status_code == 403

    def test_update_product(self, client, admin_headers, test_product):
        product_id = test_product["id"]
        resp = client.put(
            f"/api/store/products/{product_id}",
            headers=admin_headers,
            json={"selling_price": 350.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["selling_price"] == 350.0

    def test_list_products_with_category_filter(self, client, admin_headers):
        resp = client.get(
            "/api/store/products?category=fish",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_generate_barcode(self, client, admin_headers, test_product):
        product_id = test_product["id"]
        resp = client.post(
            f"/api/store/products/{product_id}/barcode",
            headers=admin_headers,
            json={"product_id": product_id, "prefix": "SFN"},
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "barcode" in data


# ═══════════════════════════════════════════════════════════════
# PRICE RULES
# ═══════════════════════════════════════════════════════════════
class TestPriceRules:
    def test_list_price_rules(self, client, admin_headers):
        resp = client.get("/api/store/price-rules", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_price_rule(self, client, admin_headers, test_product):
        resp = client.post(
            "/api/store/price-rules",
            headers=admin_headers,
            json={
                "rule_name": "Bulk Discount 10%",
                "product_id": test_product["id"],
                "rule_type": "bulk_discount",
                "min_quantity": 10.0,
                "discount_pct": 10.0,
                "is_active": True,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "id" in data

    def test_delete_price_rule(self, client, admin_headers, test_product):
        # Create then delete
        create_resp = client.post(
            "/api/store/price-rules",
            headers=admin_headers,
            json={
                "rule_name": "Temp Rule",
                "product_id": test_product["id"],
                "rule_type": "bulk_discount",
                "min_quantity": 5.0,
                "discount_pct": 5.0,
                "is_active": True,
            },
        )
        assert create_resp.status_code in (200, 201)
        rule_id = create_resp.json()["id"]

        del_resp = client.delete(
            f"/api/store/price-rules/{rule_id}",
            headers=admin_headers,
        )
        assert del_resp.status_code in (200, 204)

    def test_delete_nonexistent_rule(self, client, admin_headers):
        resp = client.delete("/api/store/price-rules/99999", headers=admin_headers)
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# STORE STOCK
# ═══════════════════════════════════════════════════════════════
class TestStoreStock:
    def test_list_stock(self, client, admin_headers):
        resp = client.get("/api/store/stock", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        items = data if isinstance(data, list) else data.get("items", [])
        assert len(items) >= 2  # seeded in conftest

    def test_get_stock_by_product(self, client, admin_headers, test_product):
        product_id = test_product["id"]
        resp = client.get(f"/api/store/stock/{product_id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "current_qty" in data

    def test_get_stock_product_not_found(self, client, admin_headers):
        resp = client.get("/api/store/stock/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_low_stock_endpoint(self, client, admin_headers):
        resp = client.get("/api/store/stock/low", headers=admin_headers)
        assert resp.status_code == 200

    def test_adjust_stock(self, client, admin_headers, test_product):
        product_id = test_product["id"]
        resp = client.post(
            "/api/store/stock/adjust",
            headers=admin_headers,
            json={
                "product_id": product_id,
                "adjustment_qty": 5.0,
                "adjustment_type": "add",
                "reason": "Test adjustment",
            },
        )
        assert resp.status_code in (200, 201)

    def test_receive_stock(self, client, admin_headers, test_product):
        from datetime import datetime, timezone

        product_id = test_product["id"]
        # First create a supply transfer (created with status="in_transit")
        transfer_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": datetime.now(timezone.utc).isoformat(),
                "source_type": "farm_produced",
                "product_id": product_id,
                "product_name": test_product["name"],
                "quantity_transferred": 10.0,
                "unit": test_product.get("unit", "kg"),
                "quality_grade": "A",
                "cost_per_unit": 170.0,
                "notes": "Test transfer for receive",
            },
        )
        assert transfer_resp.status_code == 201, f"Transfer creation failed: {transfer_resp.text}"
        transfer_id = transfer_resp.json()["id"]

        # Now receive stock from that transfer
        resp = client.post(
            f"/api/store/stock/receive?transfer_id={transfer_id}",
            headers=admin_headers,
        )
        assert resp.status_code in (200, 201)

    def test_stock_unauthenticated(self, client):
        resp = client.get("/api/store/stock")
        assert resp.status_code == 401
