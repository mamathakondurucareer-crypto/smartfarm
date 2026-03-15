"""Functional tests for aquaculture API endpoints."""

import pytest


class TestPonds:
    def test_list_ponds(self, client):
        # No auth required for listing ponds
        resp = client.get("/api/aquaculture/ponds")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_pond(self, client):
        resp = client.post(
            "/api/aquaculture/ponds",
            json={
                "pond_code": "TEST-P01",
                "name": "Test Pond",
                "pond_type": "earthen",
                "length_m": 25.0,
                "width_m": 20.0,
                "depth_m": 1.5,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["pond_code"] == "TEST-P01"
        assert data["name"] == "Test Pond"

    def test_create_pond_sets_area_and_volume(self, client):
        resp = client.post(
            "/api/aquaculture/ponds",
            json={
                "pond_code": "TEST-P02",
                "name": "Calc Pond",
                "pond_type": "concrete",
                "length_m": 10.0,
                "width_m": 10.0,
                "depth_m": 2.0,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["area_sqm"] == 100.0
        assert data["volume_liters"] == 200000.0

    def test_get_pond_by_id(self, client):
        create_resp = client.post(
            "/api/aquaculture/ponds",
            json={
                "pond_code": "TEST-P03",
                "name": "Get Test Pond",
                "pond_type": "concrete",
                "length_m": 15.0,
                "width_m": 10.0,
                "depth_m": 1.2,
            },
        )
        assert create_resp.status_code == 201
        pond_id = create_resp.json()["id"]
        resp = client.get(f"/api/aquaculture/ponds/{pond_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "pond" in data
        assert data["pond"]["id"] == pond_id

    def test_get_nonexistent_pond(self, client):
        resp = client.get("/api/aquaculture/ponds/99999")
        assert resp.status_code == 404

    def test_list_ponds_filters_by_status(self, client):
        resp = client.get("/api/aquaculture/ponds?status=active")
        assert resp.status_code == 200
        data = resp.json()
        for pond in data:
            assert pond["status"] == "active"


class TestAquacultureSummary:
    def test_summary_returns_200(self, client):
        resp = client.get("/api/aquaculture/summary")
        assert resp.status_code == 200

    def test_summary_has_required_keys(self, client):
        resp = client.get("/api/aquaculture/summary")
        data = resp.json()
        assert "active_ponds" in data
        assert "total_stock" in data
        assert "total_biomass_kg" in data
