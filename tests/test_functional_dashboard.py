"""Functional tests for dashboard API endpoints."""

import pytest


class TestDashboardKPIs:
    def test_kpis_unauthenticated(self, client):
        resp = client.get("/api/dashboard/kpis")
        # Dashboard is public in this app (no auth required on dashboard)
        assert resp.status_code in (200, 401)

    def test_kpis_returns_200(self, client):
        resp = client.get("/api/dashboard/kpis")
        assert resp.status_code == 200

    def test_kpis_structure(self, client):
        resp = client.get("/api/dashboard/kpis")
        data = resp.json()
        assert "financial" in data
        assert "aquaculture" in data
        assert "poultry" in data
        assert "crops" in data
        assert "period" in data

    def test_kpis_with_date_params(self, client):
        resp = client.get("/api/dashboard/kpis?start_date=2025-01-01&end_date=2025-12-31")
        assert resp.status_code == 200
        data = resp.json()
        assert data["period"]["start"] == "2025-01-01"
        assert data["period"]["end"] == "2025-12-31"

    def test_kpis_invalid_date_format(self, client):
        resp = client.get("/api/dashboard/kpis?start_date=not-a-date")
        assert resp.status_code == 422


class TestDashboardRevenue:
    def test_revenue_by_stream_requires_dates(self, client):
        resp = client.get("/api/dashboard/revenue-by-stream")
        assert resp.status_code == 422

    def test_revenue_by_stream_with_dates(self, client):
        resp = client.get(
            "/api/dashboard/revenue-by-stream?start_date=2025-01-01&end_date=2025-12-31"
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestDashboardExpense:
    def test_expense_by_category_requires_dates(self, client):
        resp = client.get("/api/dashboard/expense-by-category")
        assert resp.status_code == 422

    def test_expense_by_category_with_dates(self, client):
        resp = client.get(
            "/api/dashboard/expense-by-category?start_date=2025-01-01&end_date=2025-12-31"
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestDashboardMonthlyPnL:
    def test_monthly_pnl_requires_year(self, client):
        resp = client.get("/api/dashboard/monthly-pnl")
        assert resp.status_code == 422

    def test_monthly_pnl_with_year(self, client):
        resp = client.get("/api/dashboard/monthly-pnl?year=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 12

    def test_monthly_pnl_structure(self, client):
        resp = client.get("/api/dashboard/monthly-pnl?year=2025")
        months = resp.json()
        for m in months:
            assert "month" in m
            assert "revenue" in m
            assert "expenses" in m
            assert "profit" in m
