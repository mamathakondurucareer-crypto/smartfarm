"""Functional tests for Water management endpoints."""

import pytest
from datetime import date


class TestWaterSources:
    def test_list_sources(self, client, admin_headers):
        resp = client.get("/api/water/sources", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_sources_unauthenticated(self, client):
        resp = client.get("/api/water/sources")
        assert resp.status_code == 401

    def test_create_source(self, client, admin_headers):
        resp = client.post(
            "/api/water/sources",
            headers=admin_headers,
            json={
                "source_name": "Bore Well 1",
                "source_type": "borewell",
                "depth_meters": 150.0,
                "location": "North Field",
                "capacity_liters": 50000.0,
                "is_active": True,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["source_name"] == "Bore Well 1"
        assert data["source_type"] == "borewell"

    def test_create_source_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/water/sources",
            headers=viewer_headers,
            json={
                "source_name": "Bore Well 2",
                "source_type": "borewell",
                "depth_meters": 100.0,
                "location": "South Field",
                "capacity_liters": 40000.0,
            },
        )
        assert resp.status_code == 403

    def test_create_source_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/water/sources",
            headers=admin_headers,
            json={
                "source_name": "Test",
            },
        )
        assert resp.status_code == 422

    def test_list_sources_active_only(self, client, admin_headers):
        resp = client.get(
            "/api/water/sources",
            headers=admin_headers,
            params={"active_only": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestWaterTanks:
    def test_list_tanks(self, client, admin_headers):
        resp = client.get("/api/water/tanks", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_tank(self, client, admin_headers):
        resp = client.post(
            "/api/water/tanks",
            headers=admin_headers,
            json={
                "name": "Storage Tank A",
                "capacity_liters": 100000.0,
                "current_level_liters": 75000.0,
                "location": "Central Area",
                "material": "concrete",
                "is_active": True,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "Storage Tank A"
        assert data["capacity_liters"] == 100000.0
        assert data["current_level_liters"] == 75000.0

    def test_create_tank_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/water/tanks",
            headers=viewer_headers,
            json={
                "name": "Storage Tank B",
                "capacity_liters": 80000.0,
                "current_level_liters": 50000.0,
                "location": "East Area",
            },
        )
        assert resp.status_code == 403

    def test_create_tank_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/water/tanks",
            headers=admin_headers,
            json={
                "name": "Test Tank",
            },
        )
        assert resp.status_code == 422

    def test_list_tanks_active_only(self, client, admin_headers):
        resp = client.get(
            "/api/water/tanks",
            headers=admin_headers,
            params={"active_only": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestIrrigationZones:
    def test_list_zones(self, client, admin_headers):
        resp = client.get("/api/water/zones", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_zone(self, client, admin_headers):
        resp = client.post(
            "/api/water/zones",
            headers=admin_headers,
            json={
                "zone_name": "North Section A",
                "area_hectares": 2.5,
                "crop_type": "rice",
                "irrigation_method": "drip",
                "soil_type": "loam",
                "location": "North Field",
                "is_active": True,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["zone_name"] == "North Section A"
        assert data["area_hectares"] == 2.5

    def test_create_zone_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/water/zones",
            headers=viewer_headers,
            json={
                "zone_name": "North Section B",
                "area_hectares": 3.0,
                "crop_type": "cotton",
                "irrigation_method": "flood",
                "soil_type": "sandy",
                "location": "North Field 2",
            },
        )
        assert resp.status_code == 403

    def test_create_zone_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/water/zones",
            headers=admin_headers,
            json={
                "zone_name": "Test Zone",
            },
        )
        assert resp.status_code == 422


class TestIrrigationLogs:
    @pytest.fixture(scope="class")
    def test_zone(self, client, admin_headers):
        resp = client.post(
            "/api/water/zones",
            headers=admin_headers,
            json={
                "zone_name": "Log Test Zone",
                "area_hectares": 1.5,
                "crop_type": "sugarcane",
                "irrigation_method": "flood",
                "soil_type": "clayey",
                "location": "Test Area",
                "is_active": True,
            },
        )
        return resp.json()

    def test_list_irrigation_logs(self, client, admin_headers):
        resp = client.get("/api/water/irrigation-logs", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_irrigation_log(self, client, admin_headers, test_zone):
        resp = client.post(
            "/api/water/irrigation-logs",
            headers=admin_headers,
            json={
                "zone_id": test_zone["id"],
                "irrigation_date": date.today().isoformat(),
                "volume_liters": 50000.0,
                "duration_minutes": 120,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["zone_id"] == test_zone["id"]
        assert data["volume_liters"] == 50000.0
        assert data["duration_minutes"] == 120

    def test_create_irrigation_log_viewer_forbidden(self, client, viewer_headers, test_zone):
        resp = client.post(
            "/api/water/irrigation-logs",
            headers=viewer_headers,
            json={
                "zone_id": test_zone["id"],
                "irrigation_date": date.today().isoformat(),
                "volume_liters": 30000.0,
                "duration_minutes": 90,
            },
        )
        assert resp.status_code == 403

    def test_create_irrigation_log_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/water/irrigation-logs",
            headers=admin_headers,
            json={
                "zone_id": 1,
            },
        )
        assert resp.status_code == 422

    def test_list_irrigation_logs_by_zone(self, client, admin_headers, test_zone):
        resp = client.get(
            "/api/water/irrigation-logs",
            headers=admin_headers,
            params={"zone_id": test_zone["id"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestWaterUsageLogs:
    @pytest.fixture(scope="class")
    def test_source(self, client, admin_headers):
        resp = client.post(
            "/api/water/sources",
            headers=admin_headers,
            json={
                "source_name": "Usage Test Well",
                "source_type": "borewell",
                "depth_meters": 120.0,
                "location": "Test Location",
                "capacity_liters": 60000.0,
                "is_active": True,
            },
        )
        return resp.json()

    def test_list_usage_logs(self, client, admin_headers):
        resp = client.get("/api/water/usage-logs", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_usage_log(self, client, admin_headers, test_source):
        resp = client.post(
            "/api/water/usage-logs",
            headers=admin_headers,
            json={
                "source_id": test_source["id"],
                "log_date": date.today().isoformat(),
                "purpose": "irrigation",
                "volume_liters": 45000.0,
                "energy_kwh": 15.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["source_id"] == test_source["id"]
        assert data["volume_liters"] == 45000.0
        assert data["energy_kwh"] == 15.0

    def test_create_usage_log_viewer_forbidden(self, client, viewer_headers, test_source):
        resp = client.post(
            "/api/water/usage-logs",
            headers=viewer_headers,
            json={
                "source_id": test_source["id"],
                "log_date": date.today().isoformat(),
                "purpose": "livestock",
                "volume_liters": 5000.0,
                "energy_kwh": 2.0,
            },
        )
        assert resp.status_code == 403

    def test_create_usage_log_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/water/usage-logs",
            headers=admin_headers,
            json={
                "source_id": 1,
            },
        )
        assert resp.status_code == 422

    def test_list_usage_logs_by_source(self, client, admin_headers, test_source):
        resp = client.get(
            "/api/water/usage-logs",
            headers=admin_headers,
            params={"source_id": test_source["id"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestWaterQualityTests:
    @pytest.fixture(scope="class")
    def test_source_for_quality(self, client, admin_headers):
        resp = client.post(
            "/api/water/sources",
            headers=admin_headers,
            json={
                "source_name": "Quality Test Well",
                "source_type": "borewell",
                "depth_meters": 110.0,
                "location": "Quality Test Area",
                "capacity_liters": 55000.0,
                "is_active": True,
            },
        )
        return resp.json()

    def test_list_quality_tests(self, client, admin_headers):
        resp = client.get("/api/water/quality-tests", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_quality_test(self, client, admin_headers, test_source_for_quality):
        resp = client.post(
            "/api/water/quality-tests",
            headers=admin_headers,
            json={
                "source_id": test_source_for_quality["id"],
                "test_date": date.today().isoformat(),
                "bod_mg_l": 2.5,
                "tss_mg_l": 150.0,
                "ph": 7.2,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["source_id"] == test_source_for_quality["id"]
        assert data["bod_mg_l"] == 2.5
        assert data["tss_mg_l"] == 150.0
        assert data["ph"] == 7.2

    def test_create_quality_test_viewer_forbidden(self, client, viewer_headers, test_source_for_quality):
        resp = client.post(
            "/api/water/quality-tests",
            headers=viewer_headers,
            json={
                "source_id": test_source_for_quality["id"],
                "test_date": date.today().isoformat(),
                "bod_mg_l": 3.0,
                "tss_mg_l": 200.0,
                "ph": 6.8,
            },
        )
        assert resp.status_code == 403

    def test_create_quality_test_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/water/quality-tests",
            headers=admin_headers,
            json={
                "source_id": 1,
            },
        )
        assert resp.status_code == 422

    def test_list_quality_tests_by_source(self, client, admin_headers, test_source_for_quality):
        resp = client.get(
            "/api/water/quality-tests",
            headers=admin_headers,
            params={"source_id": test_source_for_quality["id"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
