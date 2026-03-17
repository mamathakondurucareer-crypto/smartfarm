"""Functional tests for Vaccination management endpoints."""

import pytest
from datetime import date, timedelta


class TestVaccinationSchedules:
    def test_list_schedules(self, client, admin_headers):
        resp = client.get("/api/vaccination/schedules", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_schedules_unauthenticated(self, client):
        resp = client.get("/api/vaccination/schedules")
        assert resp.status_code == 401

    def test_create_schedule(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/schedules",
            headers=admin_headers,
            json={
                "vaccine_name": "Newcastle Disease",
                "disease_type": "viral",
                "animal_type": "poultry",
                "scheduled_date": date.today().isoformat(),
                "repeat_interval_days": 21,
                "batch_or_flock_ref": "FLOCK-001",
                "target_population": 1000,
                "notes": "Standard vaccination schedule",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["vaccine_name"] == "Newcastle Disease"
        assert data["animal_type"] == "poultry"
        assert data["repeat_interval_days"] == 21

    def test_create_schedule_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/vaccination/schedules",
            headers=viewer_headers,
            json={
                "vaccine_name": "Avian Influenza",
                "disease_type": "viral",
                "animal_type": "poultry",
                "scheduled_date": date.today().isoformat(),
                "repeat_interval_days": 30,
                "batch_or_flock_ref": "FLOCK-002",
                "target_population": 500,
            },
        )
        assert resp.status_code == 403

    def test_create_schedule_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/schedules",
            headers=admin_headers,
            json={
                "vaccine_name": "Test Vaccine",
            },
        )
        assert resp.status_code == 422

    def test_list_schedules_by_disease(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/schedules",
            headers=admin_headers,
            params={"disease_type": "viral"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_schedules_by_animal_type(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/schedules",
            headers=admin_headers,
            params={"animal_type": "poultry"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestVaccinationRecords:
    @pytest.fixture(scope="class")
    def test_schedule(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/schedules",
            headers=admin_headers,
            json={
                "vaccine_name": "FMD Vaccine",
                "disease_type": "viral",
                "animal_type": "cattle",
                "scheduled_date": date.today().isoformat(),
                "repeat_interval_days": 180,
                "batch_or_flock_ref": "HERD-001",
                "target_population": 50,
                "notes": "Foot and Mouth Disease",
            },
        )
        return resp.json()

    def test_create_vaccination_record(self, client, admin_headers, test_schedule):
        resp = client.post(
            "/api/vaccination/records",
            headers=admin_headers,
            json={
                "schedule_id": test_schedule["id"],
                "vaccination_date": date.today().isoformat(),
                "batch_or_flock_ref": "HERD-001",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["schedule_id"] == test_schedule["id"]
        assert "next_due_date" in data
        next_due = date.fromisoformat(data["next_due_date"])
        expected_due = date.today() + timedelta(days=180)
        assert next_due == expected_due

    def test_create_vaccination_record_viewer_forbidden(self, client, viewer_headers, test_schedule):
        resp = client.post(
            "/api/vaccination/records",
            headers=viewer_headers,
            json={
                "schedule_id": test_schedule["id"],
                "vaccination_date": date.today().isoformat(),
                "batch_or_flock_ref": "HERD-001",
            },
        )
        assert resp.status_code == 403

    def test_create_vaccination_record_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/records",
            headers=admin_headers,
            json={
                "schedule_id": 1,
            },
        )
        assert resp.status_code == 422

    def test_list_vaccination_records(self, client, admin_headers):
        resp = client.get("/api/vaccination/records", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_vaccination_records_due_soon(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/records/due-soon",
            headers=admin_headers,
            params={"days_threshold": 30},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_vaccination_records_by_schedule(self, client, admin_headers, test_schedule):
        resp = client.get(
            "/api/vaccination/records",
            headers=admin_headers,
            params={"schedule_id": test_schedule["id"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestDiseaseAlerts:
    def test_list_disease_alerts(self, client, admin_headers):
        resp = client.get("/api/vaccination/disease-alerts", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_disease_alert(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/disease-alerts",
            headers=admin_headers,
            json={
                "disease_name": "New Castle Disease",
                "animal_type": "poultry",
                "severity": "high",
                "affected_population": 100,
                "reported_date": date.today().isoformat(),
                "description": "Outbreak detected in section A",
                "location": "Section A",
                "recommended_action": "Immediate vaccination",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["disease_name"] == "New Castle Disease"
        assert data["severity"] == "high"

    def test_create_disease_alert_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/vaccination/disease-alerts",
            headers=viewer_headers,
            json={
                "disease_name": "Test Disease",
                "animal_type": "cattle",
                "severity": "medium",
                "affected_population": 10,
                "reported_date": date.today().isoformat(),
                "description": "Test",
                "location": "Test Location",
            },
        )
        assert resp.status_code == 403

    def test_create_disease_alert_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/disease-alerts",
            headers=admin_headers,
            json={
                "disease_name": "Test",
            },
        )
        assert resp.status_code == 422

    def test_list_disease_alerts_by_severity(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/disease-alerts",
            headers=admin_headers,
            params={"severity": "high"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_disease_alerts_by_animal_type(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/disease-alerts",
            headers=admin_headers,
            params={"animal_type": "poultry"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestTreatmentLogs:
    def test_list_treatments(self, client, admin_headers):
        resp = client.get("/api/vaccination/treatments", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_create_treatment(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/treatments",
            headers=admin_headers,
            json={
                "animal_type": "cattle",
                "treatment_type": "antibiotic",
                "medication_name": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "twice daily",
                "duration_days": 5,
                "treated_population": 25,
                "treatment_date": date.today().isoformat(),
                "reason": "Respiratory infection",
                "notes": "Follow-up in 3 days",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["medication_name"] == "Amoxicillin"
        assert data["duration_days"] == 5

    def test_create_treatment_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/vaccination/treatments",
            headers=viewer_headers,
            json={
                "animal_type": "poultry",
                "treatment_type": "vitamin",
                "medication_name": "Vitamin A",
                "dosage": "10ml",
                "frequency": "daily",
                "duration_days": 7,
                "treated_population": 100,
                "treatment_date": date.today().isoformat(),
                "reason": "Nutritional support",
            },
        )
        assert resp.status_code == 403

    def test_create_treatment_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/treatments",
            headers=admin_headers,
            json={
                "animal_type": "cattle",
            },
        )
        assert resp.status_code == 422

    def test_list_treatments_by_animal_type(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/treatments",
            headers=admin_headers,
            params={"animal_type": "cattle"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestMortalityTracking:
    def test_list_mortality_records(self, client, admin_headers):
        resp = client.get("/api/vaccination/mortality", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_record_mortality(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/mortality",
            headers=admin_headers,
            json={
                "animal_type": "poultry",
                "count": 5,
                "cause_of_death": "Disease",
                "date_of_death": date.today().isoformat(),
                "batch_or_flock_ref": "FLOCK-001",
                "age_at_death_days": 45,
                "suspected_disease": "Newcastle Disease",
                "notes": "Sudden deaths observed in morning",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["animal_type"] == "poultry"
        assert data["count"] == 5
        assert data["cause_of_death"] == "Disease"

    def test_record_mortality_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/vaccination/mortality",
            headers=viewer_headers,
            json={
                "animal_type": "cattle",
                "count": 1,
                "cause_of_death": "Accident",
                "date_of_death": date.today().isoformat(),
                "batch_or_flock_ref": "HERD-001",
                "age_at_death_days": 365,
            },
        )
        assert resp.status_code == 403

    def test_record_mortality_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/vaccination/mortality",
            headers=admin_headers,
            json={
                "animal_type": "cattle",
            },
        )
        assert resp.status_code == 422

    def test_list_mortality_by_animal_type(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/mortality",
            headers=admin_headers,
            params={"animal_type": "poultry"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_mortality_by_cause(self, client, admin_headers):
        resp = client.get(
            "/api/vaccination/mortality",
            headers=admin_headers,
            params={"cause_of_death": "Disease"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
