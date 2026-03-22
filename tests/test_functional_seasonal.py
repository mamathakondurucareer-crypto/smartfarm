"""Functional tests for Seasonal Operations Scheduler endpoints."""

import pytest
from datetime import date


class TestSeasonalTasks:
    def test_list_tasks(self, client, admin_headers):
        resp = client.get("/api/seasonal/tasks", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_tasks_unauthenticated(self, client):
        resp = client.get("/api/seasonal/tasks")
        assert resp.status_code == 401

    def test_create_task(self, client, admin_headers):
        resp = client.post(
            "/api/seasonal/tasks",
            headers=admin_headers,
            json={
                "title": "Water drain and refill — Pond 1",
                "description": "Drain 30% water and refill from bore well",
                "category": "aquaculture",
                "month": 6,
                "week": 1,
                "assigned_to": "Aquaculture Team",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["title"] == "Water drain and refill — Pond 1"
        assert data["month"] == 6
        return data["id"]

    def test_create_task_invalid_month(self, client, admin_headers):
        resp = client.post(
            "/api/seasonal/tasks",
            headers=admin_headers,
            json={
                "title": "Invalid month task",
                "category": "aquaculture",
                "month": 13,  # invalid: must be 1-12
                "week": 1,
            },
        )
        assert resp.status_code == 422

    def test_create_task_invalid_week(self, client, admin_headers):
        resp = client.post(
            "/api/seasonal/tasks",
            headers=admin_headers,
            json={
                "title": "Invalid week task",
                "category": "aquaculture",
                "month": 6,
                "week": 5,  # invalid: max 4
            },
        )
        assert resp.status_code == 422

    def test_create_task_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/seasonal/tasks",
            headers=viewer_headers,
            json={
                "title": "Forbidden task",
                "category": "crops",
                "month": 3,
                "week": 2,
            },
        )
        assert resp.status_code == 403

    def test_current_month_tasks(self, client, admin_headers):
        resp = client.get("/api/seasonal/tasks/current-month", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_upcoming_tasks(self, client, admin_headers):
        resp = client.get("/api/seasonal/tasks/upcoming", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    def test_upcoming_tasks_custom_days(self, client, admin_headers):
        resp = client.get(
            "/api/seasonal/tasks/upcoming",
            headers=admin_headers,
            params={"days_ahead": 30},
        )
        assert resp.status_code == 200


class TestSeasonalTaskCompletions:
    def _create_task(self, client, headers, suffix="C1"):
        r = client.post(
            "/api/seasonal/tasks",
            headers=headers,
            json={
                "title": f"Task for Completion {suffix}",
                "category": "maintenance",
                "month": 3,
                "week": 2,
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_completion(self, client, admin_headers):
        task_id = self._create_task(client, admin_headers, "TC1")
        resp = client.post(
            "/api/seasonal/completions",
            headers=admin_headers,
            json={
                "task_id": task_id,
                "completion_date": str(date.today()),
                "year": date.today().year,
                "notes": "Completed as per schedule",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["task_id"] == task_id

    def test_list_completions(self, client, admin_headers):
        resp = client.get("/api/seasonal/completions", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_completions_filter_by_month(self, client, admin_headers):
        resp = client.get(
            "/api/seasonal/completions",
            headers=admin_headers,
            params={"month": 3},
        )
        assert resp.status_code == 200

    def test_completion_nonexistent_task(self, client, admin_headers):
        resp = client.post(
            "/api/seasonal/completions",
            headers=admin_headers,
            json={
                "task_id": 99999,
                "completion_date": str(date.today()),
                "year": date.today().year,
            },
        )
        assert resp.status_code in (400, 404, 422)


class TestCropRotationPlans:
    def test_create_crop_rotation(self, client, admin_headers):
        resp = client.post(
            "/api/seasonal/crop-rotation",
            headers=admin_headers,
            json={
                "field_or_zone": "Field A — 2 Acres",
                "year": date.today().year,
                "crop_name": "Turmeric",
                "variety": "Erode local",
                "sowing_month": 4,
                "harvest_month": 10,
                "area_sq_meters": 8094.0,
                "notes": "Add vermicompost before sowing",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["crop_name"] == "Turmeric"
        assert data["sowing_month"] == 4

    def test_list_crop_rotations(self, client, admin_headers):
        resp = client.get("/api/seasonal/crop-rotation", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_rotation_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/seasonal/crop-rotation",
            headers=viewer_headers,
            json={
                "field_or_zone": "Forbidden Field",
                "year": date.today().year,
                "crop_name": "Rice",
                "sowing_month": 6,
                "harvest_month": 11,
            },
        )
        assert resp.status_code == 403

    def test_create_rotation_invalid_sowing_month(self, client, admin_headers):
        resp = client.post(
            "/api/seasonal/crop-rotation",
            headers=admin_headers,
            json={
                "field_or_zone": "Invalid Field",
                "year": date.today().year,
                "crop_name": "Rice",
                "sowing_month": 0,  # invalid: min 1
                "harvest_month": 6,
            },
        )
        assert resp.status_code == 422
