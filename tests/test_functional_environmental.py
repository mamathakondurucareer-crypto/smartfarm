"""Functional tests for Environmental Monitoring Module endpoints."""

import pytest
from datetime import date, timedelta


class TestWaterOutletLogs:
    def test_create_water_outlet_log(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/water-outlet",
            headers=admin_headers,
            json={
                "log_date": str(date.today()),
                "outlet_id": "OUTLET-01",
                "location": "East Pond Discharge",
                "bod": 12.5,
                "tss": 20.0,
                "ph": 7.2,
                "turbidity": 4.5,
                "do_level": 6.8,
                "notes": "Weekly water quality check — within norms",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["outlet_id"] == "OUTLET-01"
        assert data["ph"] == 7.2

    def test_create_water_outlet_unauthenticated(self, client):
        resp = client.post(
            "/api/environmental/water-outlet",
            json={"log_date": str(date.today()), "outlet_id": "X", "bod": 5, "tss": 10, "ph": 7.0},
        )
        assert resp.status_code == 401

    def test_create_water_outlet_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/environmental/water-outlet",
            headers=viewer_headers,
            json={
                "log_date": str(date.today()),
                "outlet_id": "OUTLET-02",
                "location": "West discharge",
                "bod": 8.0,
                "tss": 15.0,
                "ph": 7.5,
            },
        )
        assert resp.status_code == 403

    def test_list_water_outlet_logs(self, client, admin_headers):
        resp = client.get("/api/environmental/water-outlet", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_water_outlet_trends(self, client, admin_headers):
        resp = client.get("/api/environmental/water-outlet/trends", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))


class TestSoilCarbonLogs:
    def test_create_soil_carbon_log(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/soil-carbon",
            headers=admin_headers,
            json={
                "log_date": str(date.today()),
                "field_id": "FIELD-A",
                "field_name": "Field A — Turmeric Block",
                "location": "North Farm",
                "soc_pct": 1.82,
                "sampling_depth_cm": 30,
                "lab_ref": "SOIL/2025/Q1/001",
                "notes": "Q1 quarterly measurement",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["soc_pct"] == 1.82
        assert data["field_id"] == "FIELD-A"

    def test_list_soil_carbon_logs(self, client, admin_headers):
        resp = client.get("/api/environmental/soil-carbon", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_soil_carbon_trend(self, client, admin_headers):
        # Create a log first so trend endpoint has data
        client.post(
            "/api/environmental/soil-carbon",
            headers=admin_headers,
            json={
                "log_date": str(date.today()),
                "field_id": "TREND-FIELD-01",
                "field_name": "Trend Test Field",
                "soc_pct": 1.65,
            },
        )
        resp = client.get(
            "/api/environmental/soil-carbon/trend",
            headers=admin_headers,
            params={"field_id": "TREND-FIELD-01"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    def test_soil_carbon_missing_required_fields(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/soil-carbon",
            headers=admin_headers,
            json={"log_date": str(date.today())},  # missing soc_pct etc
        )
        assert resp.status_code == 422


class TestPesticideApplicationLogs:
    def test_create_pesticide_log(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/pesticide-applications",
            headers=admin_headers,
            json={
                "application_date": str(date.today()),
                "field_id": "FIELD-B",
                "field_name": "Field B — Nursery",
                "active_ingredient": "Chlorpyrifos",
                "product_name": "Dursban 20EC",
                "quantity_kg": 0.5,
                "area_ha": 0.4,
                "crop_type": "nursery_seedlings",
                "applied_by": "Worker Kiran",
                "notes": "Targeted aphid control",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["active_ingredient"] == "Chlorpyrifos"
        # ai_per_ha = 0.5 / 0.4 = 1.25
        assert abs(data["ai_per_ha"] - 1.25) < 0.01

    def test_list_pesticide_logs(self, client, admin_headers):
        resp = client.get("/api/environmental/pesticide-applications", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_pesticide_summary(self, client, admin_headers):
        resp = client.get("/api/environmental/pesticide-applications/summary", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)


class TestWasteDiversionLogs:
    def test_create_waste_diversion_log(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/waste-diversion",
            headers=admin_headers,
            json={
                "log_date": str(date.today().replace(day=1)),
                "total_waste_kg": 2400.0,
                "diverted_kg": 2310.0,
                "landfill_kg": 90.0,
                "notes": "Monthly waste audit — composting and biogas",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["total_waste_kg"] == 2400.0
        # diversion_rate = 2310/2400 * 100 = 96.25%
        assert data["diversion_rate_pct"] > 95.0

    def test_list_waste_diversion(self, client, admin_headers):
        resp = client.get("/api/environmental/waste-diversion", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_waste_diversion_monthly(self, client, admin_headers):
        resp = client.get("/api/environmental/waste-diversion/monthly", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    def test_diversion_rate_target_check(self, client, admin_headers):
        """Target is >95% diversion rate."""
        resp = client.post(
            "/api/environmental/waste-diversion",
            headers=admin_headers,
            json={
                "log_date": str((date.today() - timedelta(days=30)).replace(day=1)),
                "total_waste_kg": 1000.0,
                "diverted_kg": 960.0,
                "landfill_kg": 40.0,
                "notes": "Previous month — above target",
            },
        )
        assert resp.status_code in (200, 201)
        assert resp.json()["diversion_rate_pct"] == 96.0


class TestBiodiversityLogs:
    def test_create_biodiversity_survey(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/biodiversity",
            headers=admin_headers,
            json={
                "survey_date": str(date.today()),
                "survey_type": "bird",
                "location": "Farm perimeter — East boundary",
                "species_count": 12,
                "individual_count": 47,
                "surveyor": "Ecologist Prasanna",
                "conditions": "Clear morning, 7-9 AM",
                "notes": "Q1 bird count — 3 migratory species observed",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["survey_type"] == "bird"
        assert data["species_count"] == 12

    def test_create_pollinator_survey(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/biodiversity",
            headers=admin_headers,
            json={
                "survey_date": str(date.today()),
                "survey_type": "pollinator",
                "location": "Nursery flowering zone",
                "species_count": 5,
                "individual_count": 130,
                "surveyor": "Agronomist Rekha",
                "conditions": "Peak bloom — midday transect",
                "notes": "Honeybees dominant, butterflies present",
            },
        )
        assert resp.status_code in (200, 201)
        assert resp.json()["survey_type"] == "pollinator"

    def test_list_biodiversity_logs(self, client, admin_headers):
        resp = client.get("/api/environmental/biodiversity", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_biodiversity_viewer_forbidden_create(self, client, viewer_headers):
        resp = client.post(
            "/api/environmental/biodiversity",
            headers=viewer_headers,
            json={
                "survey_date": str(date.today()),
                "survey_type": "general",
                "location": "Test",
                "species_count": 1,
                "individual_count": 1,
                "surveyor": "Viewer",
                "conditions": "Test",
            },
        )
        assert resp.status_code == 403


class TestSolarNetSurplus:
    def test_create_solar_surplus_log(self, client, admin_headers):
        resp = client.post(
            "/api/environmental/solar-surplus",
            headers=admin_headers,
            json={
                "log_date": str(date.today()),
                "generation_kwh": 120.5,
                "consumption_kwh": 85.0,
                "grid_export_kwh": 35.5,
                "notes": "Good sunshine day",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["generation_kwh"] == 120.5
        # net_surplus = 120.5 - 85.0 = 35.5
        assert abs(data["net_surplus_kwh"] - 35.5) < 0.01

    def test_list_solar_surplus(self, client, admin_headers):
        resp = client.get("/api/environmental/solar-surplus", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_carbon_report(self, client, admin_headers):
        resp = client.get("/api/environmental/solar-surplus/carbon-report", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)


class TestEnvironmentalSummary:
    def test_summary(self, client, admin_headers):
        resp = client.get("/api/environmental/summary", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_summary_unauthenticated(self, client):
        resp = client.get("/api/environmental/summary")
        assert resp.status_code == 401
