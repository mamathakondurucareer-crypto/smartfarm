"""Functional tests for HR management endpoints."""

import pytest
from datetime import date, datetime, timedelta


class TestLeaveRequests:
    def test_list_leave_requests(self, client, admin_headers):
        resp = client.get("/api/hr/leave-requests", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_leave_requests_unauthenticated(self, client):
        resp = client.get("/api/hr/leave-requests")
        assert resp.status_code == 401

    def test_create_leave_request(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/leave-requests",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "leave_type": "sick",
                "start_date": today.isoformat(),
                "days": 2,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["employee_id"] == worker_id
        assert data["leave_type"] == "sick"
        assert data["days"] == 2
        assert data["status"] == "pending"

    def test_create_leave_request_viewer_forbidden(self, client, viewer_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/leave-requests",
            headers=viewer_headers,
            json={
                "employee_id": worker_id,
                "leave_type": "casual",
                "start_date": today.isoformat(),
                "days": 1,
            },
        )
        assert resp.status_code == 403

    def test_create_leave_request_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/hr/leave-requests",
            headers=admin_headers,
            json={
                "leave_type": "sick",
            },
        )
        assert resp.status_code == 422

    def test_approve_leave_request(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        create_resp = client.post(
            "/api/hr/leave-requests",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "leave_type": "casual",
                "start_date": today.isoformat(),
                "days": 3,
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/hr/leave-requests/{request_id}/approve",
            headers=admin_headers,
            params={"status": "approved"},
        )
        assert resp.status_code == 200

    def test_reject_leave_request(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        create_resp = client.post(
            "/api/hr/leave-requests",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "leave_type": "unpaid",
                "start_date": today.isoformat(),
                "days": 1,
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/hr/leave-requests/{request_id}/approve",
            headers=admin_headers,
            params={"status": "rejected"},
        )
        assert resp.status_code == 200

    def test_list_leave_requests_by_type(self, client, admin_headers):
        resp = client.get(
            "/api/hr/leave-requests",
            headers=admin_headers,
            params={"leave_type": "sick"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestAttendance:
    def test_list_attendance(self, client, admin_headers):
        resp = client.get("/api/hr/attendance", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_attendance_unauthenticated(self, client):
        resp = client.get("/api/hr/attendance")
        assert resp.status_code == 401

    def test_mark_attendance_present(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/attendance",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "date": today.isoformat(),
                "status": "present",
                "overtime_hours": 0.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["employee_id"] == worker_id
        assert data["status"] == "present"

    def test_mark_attendance_half_day(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/attendance",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "date": today.isoformat(),
                "status": "half_day",
                "overtime_hours": 0.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["status"] == "half_day"

    def test_mark_attendance_with_overtime(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/attendance",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "date": today.isoformat(),
                "status": "present",
                "overtime_hours": 2.5,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["overtime_hours"] == 2.5

    def test_mark_attendance_viewer_forbidden(self, client, viewer_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/attendance",
            headers=viewer_headers,
            json={
                "employee_id": worker_id,
                "date": today.isoformat(),
                "status": "present",
                "overtime_hours": 0.0,
            },
        )
        assert resp.status_code == 403

    def test_mark_attendance_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/hr/attendance",
            headers=admin_headers,
            json={
                "employee_id": 1,
            },
        )
        assert resp.status_code == 422

    def test_list_attendance_by_date(self, client, admin_headers):
        today = date.today()
        resp = client.get(
            "/api/hr/attendance",
            headers=admin_headers,
            params={"date": today.isoformat()},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestPayroll:
    def test_list_payroll(self, client, admin_headers):
        resp = client.get("/api/hr/payroll", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_payroll_unauthenticated(self, client):
        resp = client.get("/api/hr/payroll")
        assert resp.status_code == 401

    def test_run_payroll(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/payroll/run",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "month": today.month,
                "year": today.year,
                "other_allowances": 5000.0,
                "tds": 1000.0,
                "other_deductions": 500.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["employee_id"] == worker_id
        assert data["month"] == today.month
        assert data["year"] == today.year
        assert "gross_salary" in data
        assert "pf_deduction" in data
        assert "net_salary" in data

    def test_run_payroll_pf_calculation(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/payroll/run",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "month": today.month,
                "year": today.year,
                "other_allowances": 0.0,
                "tds": 0.0,
                "other_deductions": 0.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        pf = data.get("pf_deduction", 0)
        assert pf >= 0

    def test_run_payroll_viewer_forbidden(self, client, viewer_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        resp = client.post(
            "/api/hr/payroll/run",
            headers=viewer_headers,
            json={
                "employee_id": worker_id,
                "month": today.month,
                "year": today.year,
                "other_allowances": 0.0,
                "tds": 0.0,
                "other_deductions": 0.0,
            },
        )
        assert resp.status_code == 403

    def test_run_payroll_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/hr/payroll/run",
            headers=admin_headers,
            json={
                "employee_id": 1,
            },
        )
        assert resp.status_code == 422

    def test_update_payroll_status_processed(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        create_resp = client.post(
            "/api/hr/payroll/run",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "month": today.month,
                "year": today.year,
                "other_allowances": 0.0,
                "tds": 0.0,
                "other_deductions": 0.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        payroll_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/hr/payroll/{payroll_id}/status",
            headers=admin_headers,
            params={"status": "processed"},
        )
        assert resp.status_code == 200

    def test_update_payroll_status_paid(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        today = date.today()
        create_resp = client.post(
            "/api/hr/payroll/run",
            headers=admin_headers,
            json={
                "employee_id": worker_id,
                "month": today.month,
                "year": today.year,
                "other_allowances": 2000.0,
                "tds": 500.0,
                "other_deductions": 200.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        payroll_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/hr/payroll/{payroll_id}/status",
            headers=admin_headers,
            params={"status": "paid"},
        )
        assert resp.status_code == 200

    def test_list_payroll_by_employee(self, client, admin_headers, user_ids):
        worker_id = user_ids["worker"]
        resp = client.get(
            "/api/hr/payroll",
            headers=admin_headers,
            params={"employee_id": worker_id},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_payroll_by_month(self, client, admin_headers):
        today = date.today()
        resp = client.get(
            "/api/hr/payroll",
            headers=admin_headers,
            params={"month": today.month, "year": today.year},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
