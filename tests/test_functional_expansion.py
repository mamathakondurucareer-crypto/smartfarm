"""Functional tests for Expansion Planning Module endpoints."""

import pytest
from datetime import date, timedelta


class TestExpansionPhases:
    def test_list_phases(self, client, admin_headers):
        resp = client.get("/api/expansion/phases", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_phases_unauthenticated(self, client):
        resp = client.get("/api/expansion/phases")
        assert resp.status_code == 401

    def test_create_phase(self, client, admin_headers):
        resp = client.post(
            "/api/expansion/phases",
            headers=admin_headers,
            json={
                "name": "Year 5 Phase 1 — Aquaculture Expansion",
                "year": 2026,
                "description": "Expand aquaculture to 20 ponds",
                "planned_start": str(date.today()),
                "planned_end": str(date.today() + timedelta(days=365)),
                "total_budget": 5000000.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "Year 5 Phase 1 — Aquaculture Expansion"
        assert data["total_budget"] == 5000000.0
        return data["id"]

    def test_create_phase_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/expansion/phases",
            headers=viewer_headers,
            json={
                "name": "Forbidden Phase",
                "year": 2027,
                "planned_start": str(date.today()),
                "planned_end": str(date.today() + timedelta(days=90)),
                "total_budget": 100000.0,
            },
        )
        assert resp.status_code == 403

    def test_update_phase_status(self, client, admin_headers):
        r = client.post(
            "/api/expansion/phases",
            headers=admin_headers,
            json={
                "name": "Status Test Phase",
                "year": 2026,
                "planned_start": str(date.today()),
                "planned_end": str(date.today() + timedelta(days=180)),
                "total_budget": 2000000.0,
            },
        )
        assert r.status_code in (200, 201)
        phase_id = r.json()["id"]
        resp = client.put(
            f"/api/expansion/phases/{phase_id}/status",
            headers=admin_headers,
            params={"status": "in_progress"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_update_nonexistent_phase_status(self, client, admin_headers):
        resp = client.put(
            "/api/expansion/phases/99999/status",
            headers=admin_headers,
            params={"status": "completed"},
        )
        assert resp.status_code == 404


class TestExpansionMilestones:
    def _create_phase(self, client, headers, suffix="M1"):
        r = client.post(
            "/api/expansion/phases",
            headers=headers,
            json={
                "name": f"Milestone Phase {suffix}",
                "year": 2026,
                "planned_start": str(date.today()),
                "planned_end": str(date.today() + timedelta(days=365)),
                "total_budget": 1000000.0,
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_milestone(self, client, admin_headers):
        phase_id = self._create_phase(client, admin_headers, "MS1")
        resp = client.post(
            "/api/expansion/milestones",
            headers=admin_headers,
            json={
                "phase_id": phase_id,
                "title": "Land acquisition complete",
                "description": "Purchase 5 acres adjacent land",
                "due_date": str(date.today() + timedelta(days=90)),
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["title"] == "Land acquisition complete"
        return data["id"]

    def test_list_milestones(self, client, admin_headers):
        resp = client.get("/api/expansion/milestones", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_complete_milestone(self, client, admin_headers):
        phase_id = self._create_phase(client, admin_headers, "MS2")
        r = client.post(
            "/api/expansion/milestones",
            headers=admin_headers,
            json={
                "phase_id": phase_id,
                "title": "Pond construction complete",
                "due_date": str(date.today() + timedelta(days=60)),
            },
        )
        assert r.status_code in (200, 201)
        milestone_id = r.json()["id"]
        resp = client.put(
            f"/api/expansion/milestones/{milestone_id}/complete",
            headers=admin_headers,
            params={"completion_notes": "All ponds built on schedule"},
        )
        assert resp.status_code == 200
        assert resp.json()["is_completed"] == True

    def test_complete_nonexistent_milestone(self, client, admin_headers):
        resp = client.put(
            "/api/expansion/milestones/99999/complete",
            headers=admin_headers,
        )
        assert resp.status_code == 404


class TestExpansionCapex:
    def _create_phase(self, client, headers, suffix="CPX"):
        r = client.post(
            "/api/expansion/phases",
            headers=headers,
            json={
                "name": f"CapEx Phase {suffix}",
                "year": 2026,
                "planned_start": str(date.today()),
                "planned_end": str(date.today() + timedelta(days=365)),
                "total_budget": 3000000.0,
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_capex_entry(self, client, admin_headers):
        phase_id = self._create_phase(client, admin_headers, "CPX1")
        resp = client.post(
            "/api/expansion/capex",
            headers=admin_headers,
            json={
                "phase_id": phase_id,
                "item_name": "20 HP Aerator Pumps",
                "category": "equipment",
                "budgeted_amount": 200000.0,
                "actual_amount": 185000.0,
                "subsidy_amount": 74000.0,
                "purchase_date": str(date.today()),
                "vendor": "Rauer Pumps Pvt Ltd",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["actual_amount"] == 185000.0
        # net_cost = 185000 - 74000 = 111000
        assert data["net_cost"] == 111000.0
        return data["id"]

    def test_list_capex(self, client, admin_headers):
        resp = client.get("/api/expansion/capex", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_budget_vs_actual(self, client, admin_headers):
        resp = client.get("/api/expansion/capex/budget-vs-actual", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (dict, list))

    def test_capex_zero_subsidy(self, client, admin_headers):
        phase_id = self._create_phase(client, admin_headers, "CPX2")
        resp = client.post(
            "/api/expansion/capex",
            headers=admin_headers,
            json={
                "phase_id": phase_id,
                "item_name": "Office Furniture",
                "category": "civil",
                "budgeted_amount": 50000.0,
                "actual_amount": 48000.0,
                "subsidy_amount": 0.0,
                "purchase_date": str(date.today()),
                "vendor": "Local Vendor",
            },
        )
        assert resp.status_code in (200, 201)
        assert resp.json()["net_cost"] == 48000.0


class TestExpansionAnalytics:
    def test_timeline(self, client, admin_headers):
        resp = client.get("/api/expansion/timeline", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), (list, dict))

    def test_readiness_score(self, client, admin_headers):
        resp = client.get("/api/expansion/readiness-score", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_readiness_score_range(self, client, admin_headers):
        resp = client.get("/api/expansion/readiness-score", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        # Score is in overall_readiness_score
        score = data.get("overall_readiness_score", data.get("readiness_score", data.get("score", 0)))
        assert 0.0 <= score <= 100.0
