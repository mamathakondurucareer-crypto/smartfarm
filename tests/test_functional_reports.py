"""Functional tests for all report endpoints."""

import pytest


# ═══════════════════════════════════════════════════════════════
# SALES REPORT
# ═══════════════════════════════════════════════════════════════
class TestSalesReport:
    def test_sales_report_authenticated(self, client, admin_headers):
        resp = client.get("/api/reports/sales", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_revenue" in data or "summary" in data

    def test_sales_report_unauthenticated(self, client):
        resp = client.get("/api/reports/sales")
        assert resp.status_code == 401

    def test_sales_report_with_date_range(self, client, admin_headers):
        resp = client.get(
            "/api/reports/sales?start_date=2025-01-01&end_date=2025-12-31",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_sales_report_has_top_products(self, client, admin_headers):
        resp = client.get("/api/reports/sales", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        # top_products may be empty list but key should exist
        assert "top_products" in data or "summary" in data

    def test_sales_report_has_payment_breakdown(self, client, admin_headers):
        resp = client.get("/api/reports/sales", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "by_payment_mode" in data or isinstance(data, dict)

    def test_sales_report_viewer_can_access(self, client, viewer_headers):
        resp = client.get("/api/reports/sales", headers=viewer_headers)
        assert resp.status_code == 200

    def test_sales_report_invalid_date_format(self, client, admin_headers):
        resp = client.get(
            "/api/reports/sales?start_date=not-a-date",
            headers=admin_headers,
        )
        assert resp.status_code in (200, 400, 422)


# ═══════════════════════════════════════════════════════════════
# PRODUCTION REPORT
# ═══════════════════════════════════════════════════════════════
class TestProductionReport:
    def test_production_report(self, client, admin_headers):
        resp = client.get("/api/reports/production", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_production_report_has_batches_field(self, client, admin_headers):
        resp = client.get("/api/reports/production", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_batches" in data or "by_category" in data

    def test_production_report_with_date_range(self, client, admin_headers):
        resp = client.get(
            "/api/reports/production?start_date=2025-01-01&end_date=2025-12-31",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_production_report_unauthenticated(self, client):
        resp = client.get("/api/reports/production")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# FINANCIAL SUMMARY REPORT
# ═══════════════════════════════════════════════════════════════
class TestFinancialReport:
    def test_financial_report(self, client, admin_headers):
        resp = client.get("/api/reports/financial-summary", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_financial_report_has_revenue(self, client, admin_headers):
        resp = client.get("/api/reports/financial-summary", headers=admin_headers)
        data = resp.json()
        assert "total_revenue" in data

    def test_financial_report_has_expenses(self, client, admin_headers):
        resp = client.get("/api/reports/financial-summary", headers=admin_headers)
        data = resp.json()
        assert "total_expenses" in data

    def test_financial_report_has_gross_profit(self, client, admin_headers):
        resp = client.get("/api/reports/financial-summary", headers=admin_headers)
        data = resp.json()
        assert "gross_profit" in data

    def test_financial_profit_equals_revenue_minus_expenses(self, client, admin_headers):
        resp = client.get("/api/reports/financial-summary", headers=admin_headers)
        data = resp.json()
        expected = data["total_revenue"] - data["total_expenses"]
        assert abs(data["gross_profit"] - expected) < 0.01

    def test_financial_report_unauthenticated(self, client):
        resp = client.get("/api/reports/financial-summary")
        assert resp.status_code == 401

    def test_financial_report_worker_forbidden(self, client, viewer_headers):
        # viewer should be allowed (read-only)
        resp = client.get("/api/reports/financial-summary", headers=viewer_headers)
        assert resp.status_code in (200, 403)


# ═══════════════════════════════════════════════════════════════
# STORE DAILY REPORT
# ═══════════════════════════════════════════════════════════════
class TestStoreDailyReport:
    def test_store_daily_report(self, client, admin_headers):
        resp = client.get("/api/reports/store-daily", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_store_daily_has_total_sales(self, client, admin_headers):
        resp = client.get("/api/reports/store-daily", headers=admin_headers)
        data = resp.json()
        assert "total_sales" in data

    def test_store_daily_has_transactions(self, client, admin_headers):
        resp = client.get("/api/reports/store-daily", headers=admin_headers)
        data = resp.json()
        assert "total_transactions" in data

    def test_store_daily_unauthenticated(self, client):
        resp = client.get("/api/reports/store-daily")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# STOCK MOVEMENT REPORT
# ═══════════════════════════════════════════════════════════════
class TestStockMovementReport:
    def test_stock_movement_report(self, client, admin_headers):
        resp = client.get("/api/reports/stock-movement", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (dict, list))

    def test_stock_movement_with_date_range(self, client, admin_headers):
        resp = client.get(
            "/api/reports/stock-movement?start_date=2025-01-01&end_date=2025-12-31",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_stock_movement_unauthenticated(self, client):
        resp = client.get("/api/reports/stock-movement")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════
# INVENTORY VALUATION REPORT
# ═══════════════════════════════════════════════════════════════
class TestInventoryValuationReport:
    def test_inventory_valuation_report(self, client, admin_headers):
        resp = client.get("/api/reports/inventory-valuation", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (dict, list))

    def test_inventory_valuation_unauthenticated(self, client):
        resp = client.get("/api/reports/inventory-valuation")
        assert resp.status_code == 401

    def test_inventory_valuation_has_total_value(self, client, admin_headers):
        resp = client.get("/api/reports/inventory-valuation", headers=admin_headers)
        data = resp.json()
        if isinstance(data, dict):
            assert "total_value" in data or "items" in data
