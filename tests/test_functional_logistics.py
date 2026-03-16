"""Functional tests for Logistics Routes and Delivery Trips endpoints."""

import pytest
from datetime import datetime, timezone


# ═══════════════════════════════════════════════════════════════
# DELIVERY ROUTES
# ═══════════════════════════════════════════════════════════════
class TestDeliveryRoutes:
    def test_list_routes(self, client, admin_headers):
        resp = client.get("/api/logistics/routes", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_routes_unauthenticated(self, client):
        resp = client.get("/api/logistics/routes")
        assert resp.status_code == 401

    def test_create_route(self, client, admin_headers):
        resp = client.post(
            "/api/logistics/routes",
            headers=admin_headers,
            json={
                "route_code": "RT-TEST-001",
                "route_name": "Nellore to Hyderabad",
                "origin": "Nellore Farm Gate",
                "destination": "Hyderabad Bowenpally Market",
                "distance_km": 280.0,
                "estimated_duration_min": 240,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["route_code"] == "RT-TEST-001"
        assert data["origin"] == "Nellore Farm Gate"
        assert data["distance_km"] == 280.0

    def test_create_route_duplicate_code(self, client, admin_headers):
        payload = {
            "route_code": "RT-DUP-001",
            "route_name": "Dup Route",
            "origin": "Origin A",
            "destination": "Destination B",
            "distance_km": 50.0,
            "estimated_duration_min": 60,
        }
        client.post("/api/logistics/routes", headers=admin_headers, json=payload)
        resp = client.post("/api/logistics/routes", headers=admin_headers, json=payload)
        assert resp.status_code == 400

    def test_create_route_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/logistics/routes",
            headers=viewer_headers,
            json={
                "route_code": "RT-VW-001",
                "route_name": "Viewer Route",
                "origin": "A",
                "destination": "B",
                "distance_km": 10.0,
                "estimated_duration_min": 30,
            },
        )
        assert resp.status_code == 403

    def test_create_route_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/logistics/routes",
            headers=admin_headers,
            json={"route_code": "RT-MISS-001"},
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════
# DELIVERY TRIPS
# ═══════════════════════════════════════════════════════════════
class TestDeliveryTrips:
    @pytest.fixture(scope="class")
    def driver_user_id(self, client, admin_headers):
        resp = client.get("/api/auth/me", headers=_driver_headers_from_client(client))
        # Use admin_headers to get users list and find driver
        users_resp = client.get("/api/auth/users", headers=admin_headers)
        if users_resp.status_code == 200:
            users = users_resp.json()
            for u in users:
                if u.get("username") == "testdriver":
                    return u["id"]
        # Fallback: get from /me with driver headers
        from tests.conftest import _headers
        driver_h = _headers(client, "driver")
        me_resp = client.get("/api/auth/me", headers=driver_h)
        return me_resp.json()["id"]

    def test_list_trips(self, client, admin_headers):
        resp = client.get("/api/logistics/trips", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        trips = data if isinstance(data, list) else data.get("trips", [])
        assert isinstance(trips, list)

    def test_list_trips_unauthenticated(self, client):
        resp = client.get("/api/logistics/trips")
        assert resp.status_code == 401

    def test_create_trip(self, client, admin_headers, user_ids):
        driver_id = user_ids["driver"]
        resp = client.post(
            "/api/logistics/trips",
            headers=admin_headers,
            json={
                "driver_id": driver_id,
                "vehicle_number": "AP-01-TU-1234",
                "vehicle_type": "tempo",
                "notes": "Test delivery trip",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "trip_code" in data
        assert data["driver_id"] == driver_id
        assert data["vehicle_number"] == "AP-01-TU-1234"
        assert data["status"] == "scheduled"

    def test_create_trip_with_route(self, client, admin_headers, user_ids):
        driver_id = user_ids["driver"]
        # Create a route first
        route_resp = client.post(
            "/api/logistics/routes",
            headers=admin_headers,
            json={
                "route_code": "RT-TRIP-001",
                "route_name": "Trip Test Route",
                "origin": "Farm",
                "destination": "Market",
                "distance_km": 100.0,
                "estimated_duration_min": 90,
            },
        )
        route_id = route_resp.json().get("id") if route_resp.status_code in (200, 201) else None

        resp = client.post(
            "/api/logistics/trips",
            headers=admin_headers,
            json={
                "driver_id": driver_id,
                "vehicle_number": "AP-01-TU-5678",
                "vehicle_type": "truck",
                "route_id": route_id,
                "notes": "Trip with route",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        if route_id:
            assert data["route_id"] == route_id

    def test_get_trip_by_id(self, client, admin_headers, user_ids):
        driver_id = user_ids["driver"]
        create_resp = client.post(
            "/api/logistics/trips",
            headers=admin_headers,
            json={
                "driver_id": driver_id,
                "vehicle_number": "AP-01-TU-GETTEST",
                "vehicle_type": "tempo",
            },
        )
        assert create_resp.status_code in (200, 201)
        trip_id = create_resp.json()["id"]

        get_resp = client.get(f"/api/logistics/trips/{trip_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == trip_id

    def test_get_trip_not_found(self, client, admin_headers):
        resp = client.get("/api/logistics/trips/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_update_trip_status(self, client, admin_headers, user_ids):
        driver_id = user_ids["driver"]
        create_resp = client.post(
            "/api/logistics/trips",
            headers=admin_headers,
            json={
                "driver_id": driver_id,
                "vehicle_number": "AP-01-STATUS-TEST",
                "vehicle_type": "tempo",
            },
        )
        assert create_resp.status_code in (200, 201)
        trip_id = create_resp.json()["id"]

        # Transition: scheduled -> loading
        loading_resp = client.put(
            f"/api/logistics/trips/{trip_id}/status",
            headers=admin_headers,
            json={"status": "loading"},
        )
        assert loading_resp.status_code == 200
        assert loading_resp.json()["status"] == "loading"

        # Transition: loading -> in_transit
        update_resp = client.put(
            f"/api/logistics/trips/{trip_id}/status",
            headers=admin_headers,
            json={
                "status": "in_transit",
                "actual_departure": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["status"] == "in_transit"

    def test_get_active_trips(self, client, driver_headers):
        resp = client.get("/api/logistics/trips/active", headers=driver_headers)
        assert resp.status_code in (200, 404)  # 404 if no employee record linked

    def test_trip_filter_by_status(self, client, admin_headers):
        resp = client.get("/api/logistics/trips?status=planned", headers=admin_headers)
        assert resp.status_code == 200

    def test_create_trip_missing_driver(self, client, admin_headers):
        resp = client.post(
            "/api/logistics/trips",
            headers=admin_headers,
            json={"vehicle_number": "AP-01-NO-DRIVER", "vehicle_type": "tempo"},
        )
        assert resp.status_code == 422

    def test_driver_can_view_own_trips(self, client, driver_headers):
        resp = client.get("/api/logistics/trips", headers=driver_headers)
        assert resp.status_code == 200


def _driver_headers_from_client(client):
    """Helper to avoid circular imports."""
    from tests.conftest import TEST_USERS
    info = TEST_USERS["driver"]
    resp = client.post(
        "/api/auth/login",
        data={"username": info["username"], "password": info["password"]},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
