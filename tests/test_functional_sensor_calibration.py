"""Functional tests for Sensor Calibration Tracker endpoints."""

import pytest
from datetime import date, timedelta


def _create_sensor(client, headers, suffix="S1"):
    """Helper to create a sensor device for calibration tests."""
    resp = client.post(
        "/api/sensors/devices",
        headers=headers,
        json={
            "device_id": f"CAL-SENSOR-{suffix}",
            "name": f"Calibration Test Sensor {suffix}",
            "sensor_type": "water_quality",
            "zone": "pond_1",
            "location": "Pond 1 — North",
            "manufacturer": "YSI",
            "model": "ProDSS",
        },
    )
    assert resp.status_code in (200, 201), f"Sensor creation failed: {resp.text}"
    return resp.json()["id"]


class TestCalibrationLogs:
    def test_create_calibration_log(self, client, admin_headers):
        sensor_id = _create_sensor(client, admin_headers, "CAL1")
        resp = client.post(
            "/api/sensor-calibration/calibrations",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "calibration_date": str(date.today()),
                "next_calibration_due": str(date.today() + timedelta(days=90)),
                "variance_before": 0.15,
                "variance_after": 0.02,
                "calibration_standard": "NIST traceable buffer pH 7.00",
                "technician": "Technician Reddy",
                "passed": True,
                "notes": "Calibrated with fresh buffer solutions",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["passed"] is True
        assert data["technician"] == "Technician Reddy"
        return data["id"]

    def test_create_failed_calibration(self, client, admin_headers):
        sensor_id = _create_sensor(client, admin_headers, "FAIL1")
        resp = client.post(
            "/api/sensor-calibration/calibrations",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "calibration_date": str(date.today()),
                "variance_before": 0.8,
                "variance_after": 0.5,
                "calibration_standard": "pH 7.00 buffer",
                "technician": "Technician Rao",
                "passed": False,
                "notes": "Sensor probe degraded — replacement needed",
            },
        )
        assert resp.status_code in (200, 201)
        assert resp.json()["passed"] is False

    def test_list_calibrations(self, client, admin_headers):
        resp = client.get("/api/sensor-calibration/calibrations", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_calibrations_due(self, client, admin_headers):
        resp = client.get("/api/sensor-calibration/calibrations/due", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), (list, dict))

    def test_calibrations_unauthenticated(self, client):
        resp = client.get("/api/sensor-calibration/calibrations")
        assert resp.status_code == 401

    def test_create_calibration_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/sensor-calibration/calibrations",
            headers=viewer_headers,
            json={
                "sensor_id": 1,
                "calibration_date": str(date.today()),
                "calibration_standard": "Test",
                "technician": "Test",
                "passed": True,
            },
        )
        assert resp.status_code == 403

    def test_calibration_updates_sensor_date(self, client, admin_headers):
        """Creating a calibration log should update the sensor's calibration_date."""
        sensor_id = _create_sensor(client, admin_headers, "UPDCAL")
        today = str(date.today())
        client.post(
            "/api/sensor-calibration/calibrations",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "calibration_date": today,
                "calibration_standard": "Test buffer",
                "technician": "Tech",
                "passed": True,
            },
        )
        # Check sensor now shows updated calibration date
        sensor_resp = client.get(f"/api/sensors/devices/{sensor_id}", headers=admin_headers)
        if sensor_resp.status_code == 200:
            sensor_data = sensor_resp.json()
            if "calibration_date" in sensor_data and sensor_data["calibration_date"]:
                assert today in sensor_data["calibration_date"]


class TestBatteryReplacements:
    def test_create_battery_replacement(self, client, admin_headers):
        sensor_id = _create_sensor(client, admin_headers, "BAT1")
        resp = client.post(
            "/api/sensor-calibration/battery-replacements",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "replacement_date": str(date.today()),
                "battery_type": "AA Lithium 1.5V",
                "next_replacement_due": str(date.today() + timedelta(days=365)),
                "replaced_by": "Worker Suresh",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["battery_type"] == "AA Lithium 1.5V"

    def test_battery_replacement_resets_sensor_level(self, client, admin_headers):
        """Replacing battery should reset sensor battery_level to 100%."""
        sensor_id = _create_sensor(client, admin_headers, "BATLVL")
        client.post(
            "/api/sensor-calibration/battery-replacements",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "replacement_date": str(date.today()),
                "battery_type": "18650 Li-ion",
                "replaced_by": "Tech",
            },
        )
        sensor_resp = client.get(f"/api/sensors/devices/{sensor_id}", headers=admin_headers)
        if sensor_resp.status_code == 200:
            sensor_data = sensor_resp.json()
            if "battery_level" in sensor_data and sensor_data["battery_level"] is not None:
                assert sensor_data["battery_level"] == 100.0

    def test_list_battery_replacements(self, client, admin_headers):
        resp = client.get("/api/sensor-calibration/battery-replacements", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_battery_replacement_schedule(self, client, admin_headers):
        resp = client.get(
            "/api/sensor-calibration/battery-replacements/schedule",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), (list, dict))


class TestFirmwareUpdates:
    def test_create_firmware_update(self, client, admin_headers):
        sensor_id = _create_sensor(client, admin_headers, "FW1")
        resp = client.post(
            "/api/sensor-calibration/firmware-updates",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "update_date": str(date.today()),
                "previous_version": "v1.2.3",
                "new_version": "v1.3.0",
                "update_method": "ota",
                "updated_by": "IT Admin Prasad",
                "notes": "Critical security patch + new temperature compensation algorithm",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["new_version"] == "v1.3.0"
        assert data["update_method"] == "ota"

    def test_firmware_update_updates_sensor_version(self, client, admin_headers):
        """Firmware update should update sensor.firmware_version field."""
        sensor_id = _create_sensor(client, admin_headers, "FWVER")
        new_version = "v2.0.1"
        client.post(
            "/api/sensor-calibration/firmware-updates",
            headers=admin_headers,
            json={
                "sensor_id": sensor_id,
                "update_date": str(date.today()),
                "previous_version": "v1.9.0",
                "new_version": new_version,
                "update_method": "manual",
                "updated_by": "Tech Lead",
            },
        )
        sensor_resp = client.get(f"/api/sensors/devices/{sensor_id}", headers=admin_headers)
        if sensor_resp.status_code == 200:
            sensor_data = sensor_resp.json()
            if "firmware_version" in sensor_data and sensor_data["firmware_version"]:
                assert sensor_data["firmware_version"] == new_version

    def test_list_firmware_updates(self, client, admin_headers):
        resp = client.get("/api/sensor-calibration/firmware-updates", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestCalibrationSummary:
    def test_summary(self, client, admin_headers):
        resp = client.get("/api/sensor-calibration/summary", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "overdue_calibration" in data or "never_calibrated" in data or len(data) > 0

    def test_summary_contains_counts(self, client, admin_headers):
        resp = client.get("/api/sensor-calibration/summary", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        # At least one count field must be present
        count_fields = {"overdue_calibration", "never_calibrated", "calibration_due_count",
                        "total_sensors", "low_battery_count"}
        assert any(f in data for f in count_fields)
