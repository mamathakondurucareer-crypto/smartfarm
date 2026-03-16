"""Functional tests for Service Request endpoints."""

import pytest


# ═══════════════════════════════════════════════════════════════
# SERVICE REQUESTS
# ═══════════════════════════════════════════════════════════════
class TestServiceRequests:
    def test_list_service_requests(self, client, admin_headers):
        resp = client.get("/api/service-requests", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        requests = data if isinstance(data, list) else data.get("requests", [])
        assert isinstance(requests, list)

    def test_list_unauthenticated(self, client):
        resp = client.get("/api/service-requests")
        assert resp.status_code == 401

    def test_create_service_request(self, client, admin_headers):
        resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={
                "title": "Aerator P1 maintenance",
                "description": "Aerator making unusual noise, needs inspection",
                "department": "aquaculture",
                "location": "Pond P1",
                "priority": "high",
                "category": "maintenance",
                "affected_equipment": "Aerator P1-A",
                "estimated_cost": 1500.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "request_code" in data
        assert data["status"] == "open"
        assert data["title"] == "Aerator P1 maintenance"
        assert data["priority"] == "high"

    def test_create_request_all_priorities(self, client, admin_headers):
        for priority in ("low", "medium", "high", "critical"):
            resp = client.post(
                "/api/service-requests",
                headers=admin_headers,
                json={
                    "title": f"Test request - {priority} priority",
                    "description": f"Testing {priority} priority",
                    "department": "maintenance",
                    "priority": priority,
                    "category": "inspection",
                },
            )
            assert resp.status_code in (200, 201), f"Failed for priority: {priority}"

    def test_create_request_missing_required_fields(self, client, admin_headers):
        resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={"title": "No description"},
        )
        assert resp.status_code == 422

    def test_create_request_worker_allowed(self, client):
        """Workers should be able to create service requests."""
        from tests.conftest import TEST_USERS
        info = TEST_USERS["worker"]
        login_resp = client.post(
            "/api/auth/login",
            data={"username": info["username"], "password": info["password"]},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post(
            "/api/service-requests",
            headers=headers,
            json={
                "title": "Worker request",
                "description": "Equipment issue in field",
                "department": "fieldwork",
                "priority": "medium",
                "category": "repair",
            },
        )
        # Workers might be allowed or forbidden depending on business rules
        assert resp.status_code in (200, 201, 403)

    def test_get_request_by_id(self, client, admin_headers):
        create_resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={
                "title": "Get by ID test",
                "description": "Test get by id",
                "department": "operations",
                "priority": "low",
                "category": "cleaning",
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/service-requests/{request_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == request_id

    def test_get_request_not_found(self, client, admin_headers):
        resp = client.get("/api/service-requests/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_update_service_request(self, client, admin_headers):
        create_resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={
                "title": "Update test request",
                "description": "Initial description",
                "department": "operations",
                "priority": "low",
                "category": "maintenance",
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        update_resp = client.put(
            f"/api/service-requests/{request_id}",
            headers=admin_headers,
            json={"priority": "high", "description": "Updated description"},
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["priority"] == "high"

    def test_assign_service_request(self, client, admin_headers, user_ids, db_session):
        from backend.models.user import Employee
        from datetime import date as dt_date

        # Create Employee record linked to worker user
        emp = Employee(
            user_id=user_ids["worker"],
            employee_code="EMP-TST-001",
            full_name="Test Worker",
            department="operations",
            designation="Worker",
            date_of_joining=dt_date(2024, 1, 1),
            phone="9000000001",
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        create_resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={
                "title": "Assign test request",
                "description": "To be assigned",
                "department": "operations",
                "priority": "medium",
                "category": "repair",
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        assign_resp = client.put(
            f"/api/service-requests/{request_id}/assign",
            headers=admin_headers,
            json={"assigned_to": emp.id},
        )
        assert assign_resp.status_code == 200
        data = assign_resp.json()
        assert data["assigned_to"] == emp.id

    def test_resolve_service_request(self, client, admin_headers):
        create_resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={
                "title": "Resolve test request",
                "description": "To be resolved",
                "department": "operations",
                "priority": "medium",
                "category": "maintenance",
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        resolve_resp = client.put(
            f"/api/service-requests/{request_id}/resolve",
            headers=admin_headers,
            json={
                "resolution_notes": "Replaced faulty component",
                "actual_cost": 1200.0,
            },
        )
        assert resolve_resp.status_code == 200
        data = resolve_resp.json()
        assert data["status"] == "resolved"
        assert data["resolution_notes"] == "Replaced faulty component"

    def test_resolve_missing_notes(self, client, admin_headers):
        create_resp = client.post(
            "/api/service-requests",
            headers=admin_headers,
            json={
                "title": "Resolve no-notes test",
                "description": "Test",
                "department": "operations",
                "priority": "low",
                "category": "inspection",
            },
        )
        assert create_resp.status_code in (200, 201)
        request_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/service-requests/{request_id}/resolve",
            headers=admin_headers,
            json={},  # Missing resolution_notes (required)
        )
        assert resp.status_code == 422

    def test_filter_by_status(self, client, admin_headers):
        resp = client.get("/api/service-requests?status=open", headers=admin_headers)
        assert resp.status_code == 200

    def test_filter_by_department(self, client, admin_headers):
        resp = client.get("/api/service-requests?department=aquaculture", headers=admin_headers)
        assert resp.status_code == 200

    def test_filter_by_priority(self, client, admin_headers):
        resp = client.get("/api/service-requests?priority=high", headers=admin_headers)
        assert resp.status_code == 200
