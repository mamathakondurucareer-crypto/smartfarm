"""Functional tests for Agri-Tourism / Farm Visit endpoints."""

import pytest
from datetime import date, timedelta


class TestVisitPackages:
    def test_list_packages(self, client, admin_headers):
        resp = client.get("/api/agritourism/packages", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_packages_unauthenticated(self, client):
        resp = client.get("/api/agritourism/packages")
        assert resp.status_code == 401

    def test_create_package(self, client, admin_headers):
        resp = client.post(
            "/api/agritourism/packages",
            headers=admin_headers,
            json={
                "name": "Full Farm Day Tour",
                "package_type": "educational",
                "description": "Complete farm tour including fish ponds, poultry, greenhouse",
                "duration_hours": 4.0,
                "price_per_person": 500.0,
                "max_group_size": 30,
                "includes_meal": True,
                "is_active": True,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "Full Farm Day Tour"
        assert data["price_per_person"] == 500.0
        return data["id"]

    def test_create_package_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/agritourism/packages",
            headers=viewer_headers,
            json={
                "name": "Forbidden Package",
                "package_type": "general",
                "description": "Test",
                "duration_hours": 2.0,
                "price_per_person": 200.0,
                "max_group_size": 10,
            },
        )
        assert resp.status_code == 403

    def test_update_package(self, client, admin_headers):
        r = client.post(
            "/api/agritourism/packages",
            headers=admin_headers,
            json={
                "name": "Update Test Package",
                "package_type": "family",
                "description": "To be updated",
                "duration_hours": 2.0,
                "price_per_person": 300.0,
                "max_group_size": 20,
                "includes_meal": False,
                "is_active": True,
            },
        )
        pkg_id = r.json()["id"]
        resp = client.put(
            f"/api/agritourism/packages/{pkg_id}",
            headers=admin_headers,
            json={
                "name": "Update Test Package",
                "package_type": "family",
                "duration_hours": 2.0,
                "price_per_person": 350.0,
                "max_group_size": 20,
                "is_active": False,
            },
        )
        assert resp.status_code == 200


class TestVisitorGroups:
    def test_create_visitor_group(self, client, admin_headers):
        resp = client.post(
            "/api/agritourism/visitor-groups",
            headers=admin_headers,
            json={
                "group_name": "Nellore Agricultural College Batch 1",
                "group_type": "educational",
                "contact_person": "Prof. Rao",
                "contact_phone": "9876512345",
                "contact_email": "rao@college.edu",
                "city": "Nellore",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["group_type"] == "educational"
        return data["id"]

    def test_list_visitor_groups(self, client, admin_headers):
        resp = client.get("/api/agritourism/visitor-groups", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestVisitBookings:
    def _setup(self, client, headers, suffix="B1"):
        pkg = client.post(
            "/api/agritourism/packages",
            headers=headers,
            json={
                "name": f"Booking Test Package {suffix}",
                "package_type": "general",
                "description": "Test",
                "duration_hours": 3.0,
                "price_per_person": 400.0,
                "max_group_size": 25,
                "includes_meal": True,
                "is_active": True,
            },
        )
        assert pkg.status_code in (200, 201)
        pkg_id = pkg.json()["id"]

        grp = client.post(
            "/api/agritourism/visitor-groups",
            headers=headers,
            json={
                "group_name": f"Test Group {suffix}",
                "group_type": "family",
                "contact_person": "Contact Person",
                "contact_phone": "9000000099",
            },
        )
        assert grp.status_code in (200, 201)
        grp_id = grp.json()["id"]
        return pkg_id, grp_id

    def test_create_booking(self, client, admin_headers):
        pkg_id, grp_id = self._setup(client, admin_headers, "BK1")
        resp = client.post(
            "/api/agritourism/bookings",
            headers=admin_headers,
            json={
                "package_id": pkg_id,
                "visitor_group_id": grp_id,
                "visit_date": str(date.today() + timedelta(days=7)),
                "time_slot": "10:00",
                "pax_count": 10,
                "advance_paid": 2000.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["pax_count"] == 10
        # total_amount = 400 * 10 = 4000
        assert data["total_amount"] == 4000.0
        assert data["balance_due"] == 2000.0
        return data["id"]

    def test_list_bookings(self, client, admin_headers):
        resp = client.get("/api/agritourism/bookings", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_booking_availability(self, client, admin_headers):
        pkg_id, _ = self._setup(client, admin_headers, "AV1")
        resp = client.get(
            "/api/agritourism/bookings/availability",
            headers=admin_headers,
            params={"visit_date": str(date.today() + timedelta(days=14)), "package_id": pkg_id},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_confirm_booking(self, client, admin_headers):
        pkg_id, grp_id = self._setup(client, admin_headers, "CONF1")
        r = client.post(
            "/api/agritourism/bookings",
            headers=admin_headers,
            json={
                "package_id": pkg_id,
                "visitor_group_id": grp_id,
                "visit_date": str(date.today() + timedelta(days=5)),
                "time_slot": "14:00",
                "pax_count": 8,
                "advance_paid": 1600.0,
            },
        )
        assert r.status_code in (200, 201)
        booking_id = r.json()["id"]
        resp = client.put(
            f"/api/agritourism/bookings/{booking_id}/confirm",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    def test_cancel_booking(self, client, admin_headers):
        pkg_id, grp_id = self._setup(client, admin_headers, "CANC1")
        r = client.post(
            "/api/agritourism/bookings",
            headers=admin_headers,
            json={
                "package_id": pkg_id,
                "visitor_group_id": grp_id,
                "visit_date": str(date.today() + timedelta(days=3)),
                "time_slot": "09:00",
                "pax_count": 5,
                "advance_paid": 500.0,
            },
        )
        assert r.status_code in (200, 201)
        booking_id = r.json()["id"]
        resp = client.put(
            f"/api/agritourism/bookings/{booking_id}/cancel",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_complete_booking_with_feedback(self, client, admin_headers):
        pkg_id, grp_id = self._setup(client, admin_headers, "COMP1")
        r = client.post(
            "/api/agritourism/bookings",
            headers=admin_headers,
            json={
                "package_id": pkg_id,
                "visitor_group_id": grp_id,
                "visit_date": str(date.today()),
                "time_slot": "11:00",
                "pax_count": 6,
                "advance_paid": 1200.0,
            },
        )
        assert r.status_code in (200, 201)
        booking_id = r.json()["id"]
        resp = client.put(
            f"/api/agritourism/bookings/{booking_id}/complete",
            headers=admin_headers,
            params={"feedback_rating": 5, "feedback_comment": "Excellent tour!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

    def test_complete_booking_invalid_rating(self, client, admin_headers):
        pkg_id, grp_id = self._setup(client, admin_headers, "COMP2")
        r = client.post(
            "/api/agritourism/bookings",
            headers=admin_headers,
            json={
                "package_id": pkg_id,
                "visitor_group_id": grp_id,
                "visit_date": str(date.today()),
                "time_slot": "16:00",
                "pax_count": 4,
                "advance_paid": 800.0,
            },
        )
        assert r.status_code in (200, 201)
        booking_id = r.json()["id"]
        resp = client.put(
            f"/api/agritourism/bookings/{booking_id}/complete",
            headers=admin_headers,
            params={"feedback_rating": 10},  # invalid: max 5
        )
        assert resp.status_code in (400, 422)

    def test_confirm_nonexistent_booking(self, client, admin_headers):
        resp = client.put("/api/agritourism/bookings/99999/confirm", headers=admin_headers)
        assert resp.status_code == 404


class TestTourRevenue:
    def test_create_revenue_entry(self, client, admin_headers):
        pkg = client.post(
            "/api/agritourism/packages",
            headers=admin_headers,
            json={
                "name": "Revenue Test Package",
                "package_type": "general",
                "description": "Test",
                "duration_hours": 2.0,
                "price_per_person": 350.0,
                "max_group_size": 20,
                "is_active": True,
            },
        )
        assert pkg.status_code in (200, 201)
        grp = client.post(
            "/api/agritourism/visitor-groups",
            headers=admin_headers,
            json={
                "group_name": "Revenue Test Group",
                "group_type": "corporate",
                "contact_person": "Manager",
                "contact_phone": "9000000001",
            },
        )
        assert grp.status_code in (200, 201)
        booking = client.post(
            "/api/agritourism/bookings",
            headers=admin_headers,
            json={
                "package_id": pkg.json()["id"],
                "visitor_group_id": grp.json()["id"],
                "visit_date": str(date.today()),
                "time_slot": "10:00",
                "pax_count": 4,
                "advance_paid": 700.0,
            },
        )
        assert booking.status_code in (200, 201)
        booking_id = booking.json()["id"]

        resp = client.post(
            "/api/agritourism/revenue",
            headers=admin_headers,
            json={
                "booking_id": booking_id,
                "entry_date": str(date.today()),
                "amount_received": 700.0,
                "payment_mode": "upi",
                "notes": "Advance payment",
            },
        )
        assert resp.status_code in (200, 201)
        assert resp.json()["amount_received"] == 700.0

    def test_monthly_revenue_summary(self, client, admin_headers):
        resp = client.get("/api/agritourism/revenue/monthly", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "annual_target" in data or "monthly_data" in data or len(data) > 0
