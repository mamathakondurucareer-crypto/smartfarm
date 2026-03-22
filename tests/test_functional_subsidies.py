"""Functional tests for Government Subsidies endpoints."""

import pytest
from datetime import date, timedelta


class TestSubsidySchemes:
    def test_list_schemes(self, client, admin_headers):
        resp = client.get("/api/subsidies/schemes", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_schemes_unauthenticated(self, client):
        resp = client.get("/api/subsidies/schemes")
        assert resp.status_code == 401

    def test_create_scheme(self, client, admin_headers):
        resp = client.post(
            "/api/subsidies/schemes",
            headers=admin_headers,
            json={
                "scheme_code": "MNRE-SOLAR-001",
                "name": "MNRE Solar Rooftop Subsidy",
                "ministry": "MNRE",
                "category": "solar",
                "subsidy_pct": 40.0,
                "max_amount": 400000.0,
                "is_active": True,
                "description": "Central govt solar subsidy for farm installations",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["scheme_code"] == "MNRE-SOLAR-001"
        assert data["ministry"] == "MNRE"
        return data["id"]

    def test_create_scheme_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/subsidies/schemes",
            headers=viewer_headers,
            json={
                "scheme_code": "FORBIDDEN-001",
                "name": "Forbidden Scheme",
                "ministry": "Test",
                "category": "general",
            },
        )
        assert resp.status_code == 403

    def test_get_scheme_by_id(self, client, admin_headers):
        r = client.post(
            "/api/subsidies/schemes",
            headers=admin_headers,
            json={
                "scheme_code": "GET-TEST-001",
                "name": "Get Test Scheme",
                "ministry": "NABARD",
                "category": "aquaculture",
            },
        )
        assert r.status_code in (200, 201)
        scheme_id = r.json()["id"]

        resp = client.get(f"/api/subsidies/schemes/{scheme_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == scheme_id

    def test_get_nonexistent_scheme(self, client, admin_headers):
        resp = client.get("/api/subsidies/schemes/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_create_duplicate_scheme_code(self, client, admin_headers):
        payload = {
            "scheme_code": "DUPE-CODE-001",
            "name": "Duplicate Scheme",
            "ministry": "Test Ministry",
            "category": "general",
        }
        client.post("/api/subsidies/schemes", headers=admin_headers, json=payload)
        r2 = client.post("/api/subsidies/schemes", headers=admin_headers, json=payload)
        assert r2.status_code in (400, 409, 422)


class TestSubsidyApplications:
    def _create_scheme(self, client, headers, suffix="APP"):
        r = client.post(
            "/api/subsidies/schemes",
            headers=headers,
            json={
                "scheme_code": f"APP-SCHEME-{suffix}",
                "name": "App Test Scheme",
                "ministry": "MNRE",
                "category": "solar",
                "max_amount": 500000.0,
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_application(self, client, admin_headers):
        scheme_id = self._create_scheme(client, admin_headers, "CREATE1")
        resp = client.post(
            "/api/subsidies/applications",
            headers=admin_headers,
            json={
                "scheme_id": scheme_id,
                "applied_date": str(date.today()),
                "project_cost": 1000000.0,
                "claimed_subsidy_amount": 400000.0,
                "application_number": "MNRE/AP/2025/001",
                "project_description": "20kWp rooftop solar at main farm",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["project_cost"] == 1000000.0
        assert data["status"] == "submitted"
        return data["id"]

    def test_list_applications(self, client, admin_headers):
        resp = client.get("/api/subsidies/applications", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_update_application_status_approved(self, client, admin_headers):
        scheme_id = self._create_scheme(client, admin_headers, "APPROVE1")
        r = client.post(
            "/api/subsidies/applications",
            headers=admin_headers,
            json={
                "scheme_id": scheme_id,
                "applied_date": str(date.today()),
                "project_cost": 800000.0,
                "claimed_subsidy_amount": 320000.0,
            },
        )
        assert r.status_code in (200, 201)
        app_id = r.json()["id"]

        resp = client.patch(
            f"/api/subsidies/applications/{app_id}/status",
            headers=admin_headers,
            params={"status": "approved", "approved_amount": 300000.0},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    def test_update_application_status_rejected(self, client, admin_headers):
        scheme_id = self._create_scheme(client, admin_headers, "REJECT1")
        r = client.post(
            "/api/subsidies/applications",
            headers=admin_headers,
            json={
                "scheme_id": scheme_id,
                "applied_date": str(date.today()),
                "project_cost": 500000.0,
                "claimed_subsidy_amount": 200000.0,
            },
        )
        app_id = r.json()["id"]

        resp = client.patch(
            f"/api/subsidies/applications/{app_id}/status",
            headers=admin_headers,
            params={"status": "rejected", "rejection_reason": "Incomplete documentation"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    def test_update_nonexistent_application(self, client, admin_headers):
        resp = client.patch(
            "/api/subsidies/applications/99999/status",
            headers=admin_headers,
            params={"status": "approved"},
        )
        assert resp.status_code == 404


class TestDisbursements:
    def _create_approved_app(self, client, headers, suffix="D1"):
        r1 = client.post(
            "/api/subsidies/schemes",
            headers=headers,
            json={
                "scheme_code": f"DISB-SCHEME-{suffix}",
                "name": "Disbursement Scheme",
                "ministry": "MNRE",
                "category": "solar",
            },
        )
        scheme_id = r1.json()["id"]
        r2 = client.post(
            "/api/subsidies/applications",
            headers=headers,
            json={
                "scheme_id": scheme_id,
                "applied_date": str(date.today()),
                "project_cost": 1000000.0,
                "claimed_subsidy_amount": 400000.0,
            },
        )
        app_id = r2.json()["id"]
        client.patch(
            f"/api/subsidies/applications/{app_id}/status",
            headers=headers,
            params={"status": "approved", "approved_amount": 380000.0},
        )
        return app_id

    def test_create_disbursement(self, client, admin_headers):
        app_id = self._create_approved_app(client, admin_headers, "D1")
        resp = client.post(
            "/api/subsidies/disbursements",
            headers=admin_headers,
            json={
                "application_id": app_id,
                "disbursement_date": str(date.today()),
                "amount_received": 190000.0,
                "payment_mode": "bank_transfer",
                "reference_number": "DISB/2025/001",
                "notes": "First instalment received",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["amount_received"] == 190000.0

    def test_list_disbursements(self, client, admin_headers):
        resp = client.get("/api/subsidies/disbursements", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_summary(self, client, admin_headers):
        resp = client.get("/api/subsidies/summary", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), dict)
