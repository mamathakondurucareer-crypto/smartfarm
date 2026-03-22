"""Functional tests for Audit / Reporting Calendar endpoints."""

import pytest
from datetime import date, timedelta


class TestAuditLogs:
    def test_list_audit_logs(self, client, admin_headers):
        resp = client.get("/api/audit/logs", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_audit_logs_unauthenticated(self, client):
        resp = client.get("/api/audit/logs")
        assert resp.status_code == 401

    def test_list_audit_logs_viewer_forbidden(self, client, viewer_headers):
        resp = client.get("/api/audit/logs", headers=viewer_headers)
        assert resp.status_code == 403


class TestReportSchedules:
    def test_create_schedule(self, client, admin_headers):
        resp = client.post(
            "/api/audit/schedules",
            headers=admin_headers,
            json={
                "name": "Monthly Water Quality Report",
                "report_type": "water_quality",
                "frequency": "monthly",
                "next_run_date": str(date.today() + timedelta(days=30)),
                "output_format": "pdf",
                "recipients": "admin@farm.com",
                "notes": "Auto-generated monthly compliance report",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "Monthly Water Quality Report"
        assert data["frequency"] == "monthly"
        return data["id"]

    def test_create_schedule_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/audit/schedules",
            headers=viewer_headers,
            json={
                "name": "Forbidden Report",
                "report_type": "energy",
                "frequency": "weekly",
                "next_run_date": str(date.today() + timedelta(days=7)),
            },
        )
        assert resp.status_code == 403

    def test_list_schedules(self, client, admin_headers):
        resp = client.get("/api/audit/schedules", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_and_toggle_schedule(self, client, admin_headers):
        r = client.post(
            "/api/audit/schedules",
            headers=admin_headers,
            json={
                "name": "Toggle Test Report",
                "report_type": "financial",
                "frequency": "quarterly",
                "next_run_date": str(date.today() + timedelta(days=90)),
            },
        )
        assert r.status_code in (200, 201)
        schedule_id = r.json()["id"]

        resp = client.put(
            f"/api/audit/schedules/{schedule_id}/toggle",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "is_active" in resp.json()

    def test_advance_schedule(self, client, admin_headers):
        r = client.post(
            "/api/audit/schedules",
            headers=admin_headers,
            json={
                "name": "Advance Test Report",
                "report_type": "inventory",
                "frequency": "weekly",
                "next_run_date": str(date.today() + timedelta(days=7)),
            },
        )
        assert r.status_code in (200, 201)
        schedule_id = r.json()["id"]

        resp = client.put(
            f"/api/audit/schedules/{schedule_id}/advance",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert "next_run_date" in resp.json()

    def test_toggle_nonexistent_schedule(self, client, admin_headers):
        resp = client.put("/api/audit/schedules/99999/toggle", headers=admin_headers)
        assert resp.status_code == 404


class TestReportExecutions:
    def _create_schedule(self, client, headers):
        r = client.post(
            "/api/audit/schedules",
            headers=headers,
            json={
                "name": "Exec Base Report",
                "report_type": "aquaculture",
                "frequency": "monthly",
                "next_run_date": str(date.today() + timedelta(days=30)),
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_execution(self, client, admin_headers):
        schedule_id = self._create_schedule(client, admin_headers)
        resp = client.post(
            "/api/audit/executions",
            headers=admin_headers,
            json={
                "schedule_id": schedule_id,
                "report_type": "aquaculture",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["report_type"] == "aquaculture"
        assert data["status"] == "running"
        return data["id"]

    def test_list_executions(self, client, admin_headers):
        resp = client.get("/api/audit/executions", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_complete_execution(self, client, admin_headers):
        schedule_id = self._create_schedule(client, admin_headers)
        r = client.post(
            "/api/audit/executions",
            headers=admin_headers,
            json={"schedule_id": schedule_id, "report_type": "energy"},
        )
        assert r.status_code in (200, 201)
        execution_id = r.json()["id"]

        resp = client.patch(
            f"/api/audit/executions/{execution_id}/complete",
            headers=admin_headers,
            params={
                "status": "success",
                "file_url": "https://storage.farm/reports/energy_2025_06.pdf",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_complete_nonexistent_execution(self, client, admin_headers):
        resp = client.patch(
            "/api/audit/executions/99999/complete",
            headers=admin_headers,
            params={"status": "success"},
        )
        assert resp.status_code == 404

    def test_complete_execution_invalid_status(self, client, admin_headers):
        schedule_id = self._create_schedule(client, admin_headers)
        r = client.post(
            "/api/audit/executions",
            headers=admin_headers,
            json={"schedule_id": schedule_id, "report_type": "hr"},
        )
        execution_id = r.json()["id"]
        resp = client.patch(
            f"/api/audit/executions/{execution_id}/complete",
            headers=admin_headers,
            params={"status": "invalid_status"},
        )
        assert resp.status_code == 400


class TestAuditCalendar:
    def test_get_calendar(self, client, admin_headers):
        resp = client.get("/api/audit/calendar", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    def test_calendar_viewer_forbidden(self, client, viewer_headers):
        resp = client.get("/api/audit/calendar", headers=viewer_headers)
        assert resp.status_code == 403

    def test_calendar_custom_days(self, client, admin_headers):
        resp = client.get(
            "/api/audit/calendar",
            headers=admin_headers,
            params={"days_ahead": 60},
        )
        assert resp.status_code == 200
