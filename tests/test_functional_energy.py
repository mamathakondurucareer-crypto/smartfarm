"""Functional tests for Solar & Energy endpoints."""

import pytest
from datetime import date, datetime


class TestSolarArrays:
    def test_list_arrays(self, client, admin_headers):
        resp = client.get("/api/energy/arrays", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_arrays_unauthenticated(self, client):
        resp = client.get("/api/energy/arrays")
        assert resp.status_code == 401

    def test_create_array(self, client, admin_headers):
        resp = client.post(
            "/api/energy/arrays",
            headers=admin_headers,
            json={
                "name": "South Roof Array A",
                "location": "Main Building Roof",
                "panel_count": 40,
                "panel_wattage_wp": 400.0,
                "total_capacity_kwp": 16.0,
                "tilt_degrees": 15.0,
                "commissioned_date": str(date.today()),
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "South Roof Array A"
        assert data["panel_count"] == 40
        return data["id"]

    def test_create_array_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/energy/arrays",
            headers=viewer_headers,
            json={
                "name": "North Array",
                "location": "North Field",
                "panel_count": 20,
                "panel_wattage_wp": 300.0,
                "total_capacity_kwp": 6.0,
            },
        )
        assert resp.status_code == 403

    def test_create_array_missing_name(self, client, admin_headers):
        resp = client.post(
            "/api/energy/arrays",
            headers=admin_headers,
            json={},  # missing required name
        )
        assert resp.status_code == 422


class TestInverters:
    def test_list_inverters(self, client, admin_headers):
        resp = client.get("/api/energy/inverters", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_inverter(self, client, admin_headers):
        resp = client.post(
            "/api/energy/inverters",
            headers=admin_headers,
            json={
                "name": "Inverter INV-01",
                "make": "SMA",
                "model": "SB5.0-1SP",
                "rated_kva": 5.0,
                "inverter_type": "grid_tie",
                "installation_date": str(date.today()),
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "Inverter INV-01"

    def test_create_inverter_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/energy/inverters",
            headers=viewer_headers,
            json={"name": "Forbidden Inverter", "rated_kva": 3.0},
        )
        assert resp.status_code == 403


class TestGenerationLogs:
    def _create_array_id(self, client, headers):
        r = client.post(
            "/api/energy/arrays",
            headers=headers,
            json={"name": "Gen Test Array", "panel_count": 10, "panel_wattage_wp": 400.0, "total_capacity_kwp": 4.0},
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_generation_log(self, client, admin_headers):
        array_id = self._create_array_id(client, admin_headers)
        resp = client.post(
            "/api/energy/generation",
            headers=admin_headers,
            json={
                "solar_array_id": array_id,
                "log_date": str(date.today()),
                "units_generated_kwh": 85.5,
                "peak_power_kw": 14.2,
                "sunshine_hours": 6.5,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["units_generated_kwh"] == 85.5

    def test_list_generation(self, client, admin_headers):
        resp = client.get("/api/energy/generation", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_generation_summary(self, client, admin_headers):
        resp = client.get("/api/energy/generation/summary", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), (dict, list))

    def test_generation_missing_array_id(self, client, admin_headers):
        resp = client.post(
            "/api/energy/generation",
            headers=admin_headers,
            json={"log_date": str(date.today()), "units_generated_kwh": 10.0},
        )
        assert resp.status_code == 422


class TestConsumptionLogs:
    def test_create_consumption_log(self, client, admin_headers):
        resp = client.post(
            "/api/energy/consumption",
            headers=admin_headers,
            json={
                "log_date": str(date.today()),
                "section": "aquaculture",
                "units_consumed_kwh": 42.0,
                "source": "solar",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["section"] == "aquaculture"

    def test_list_consumption(self, client, admin_headers):
        resp = client.get("/api/energy/consumption", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_consumption_summary(self, client, admin_headers):
        resp = client.get("/api/energy/consumption/summary", headers=admin_headers)
        assert resp.status_code == 200

    def test_consumption_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/energy/consumption",
            headers=viewer_headers,
            json={"log_date": str(date.today()), "section": "poultry", "units_consumed_kwh": 5.0, "source": "grid"},
        )
        assert resp.status_code == 403


class TestEnergyDashboard:
    def test_dashboard(self, client, admin_headers):
        resp = client.get("/api/energy/dashboard", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), dict)


class TestBatteryBanks:
    def test_create_battery_bank(self, client, admin_headers):
        resp = client.post(
            "/api/energy/batteries",
            headers=admin_headers,
            json={
                "name": "Battery Bank 1",
                "capacity_kwh": 20.0,
                "battery_type": "lithium_ion",
                "commissioned_date": str(date.today()),
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "Battery Bank 1"
        return data["id"]

    def test_list_batteries(self, client, admin_headers):
        resp = client.get("/api/energy/batteries", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_update_battery_soc(self, client, admin_headers):
        r = client.post(
            "/api/energy/batteries",
            headers=admin_headers,
            json={"name": "SOC Test Bank", "capacity_kwh": 10.0, "battery_type": "lead_acid"},
        )
        assert r.status_code in (200, 201)
        bank_id = r.json()["id"]

        resp = client.patch(
            f"/api/energy/batteries/{bank_id}/soc",
            headers=admin_headers,
            params={"soc_pct": 85.0},
        )
        assert resp.status_code == 200

    def test_update_nonexistent_battery(self, client, admin_headers):
        resp = client.patch(
            "/api/energy/batteries/99999/soc",
            headers=admin_headers,
            params={"soc_pct": 50.0},
        )
        assert resp.status_code == 404


class TestGridEvents:
    def test_create_grid_event(self, client, admin_headers):
        resp = client.post(
            "/api/energy/grid-events",
            headers=admin_headers,
            json={
                "event_date": str(date.today()),
                "event_type": "outage",
                "duration_minutes": 45.0,
                "notes": "Scheduled maintenance by APSPDCL",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["event_type"] == "outage"

    def test_list_grid_events(self, client, admin_headers):
        resp = client.get("/api/energy/grid-events", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_grid_event_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/energy/grid-events",
            headers=viewer_headers,
            json={"event_date": str(date.today()), "event_type": "surge"},
        )
        assert resp.status_code == 403

    def test_grid_event_missing_type(self, client, admin_headers):
        resp = client.post(
            "/api/energy/grid-events",
            headers=admin_headers,
            json={"event_date": str(date.today())},  # missing event_type
        )
        assert resp.status_code == 422
