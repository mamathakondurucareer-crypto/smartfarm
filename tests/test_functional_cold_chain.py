"""Functional tests for Cold Chain Shipment Tracking endpoints."""

import pytest
from datetime import datetime, timezone, timedelta


class TestColdChainVehicles:
    def test_list_vehicles(self, client, admin_headers):
        resp = client.get("/api/cold-chain/vehicles", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_vehicles_unauthenticated(self, client):
        resp = client.get("/api/cold-chain/vehicles")
        assert resp.status_code == 401

    def test_create_vehicle(self, client, admin_headers):
        resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={
                "vehicle_number": "AP-01-CC-5001",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 2000.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["vehicle_number"] == "AP-01-CC-5001"
        assert data["refrigerated"] is True
        assert data["min_temp_c"] == 0.0

    def test_create_vehicle_duplicate(self, client, admin_headers):
        payload = {
            "vehicle_number": "AP-01-CC-DUP-001",
            "vehicle_type": "refrigerated_van",
            "capacity_kg": 2000.0,
            "refrigerated": True,
            "min_temp_c": 0.0,
            "max_temp_c": 4.0,
        }
        client.post("/api/cold-chain/vehicles", headers=admin_headers, json=payload)
        resp = client.post("/api/cold-chain/vehicles", headers=admin_headers, json=payload)
        assert resp.status_code == 400

    def test_create_vehicle_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/cold-chain/vehicles",
            headers=viewer_headers,
            json={
                "vehicle_number": "AP-01-CC-VIEW",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 1000.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        assert resp.status_code == 403

    def test_create_vehicle_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={"vehicle_number": "AP-01-CC-MISS"},
        )
        assert resp.status_code == 422

    def test_deactivate_vehicle(self, client, admin_headers):
        create_resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={
                "vehicle_number": "AP-01-CC-DEACT",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 1500.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        vehicle_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/cold-chain/vehicles/{vehicle_id}/deactivate",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_list_vehicles_refrigerated_only(self, client, admin_headers):
        resp = client.get(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            params={"refrigerated_only": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestColdChainShipments:
    @pytest.fixture(scope="class")
    def test_vehicle(self, client, admin_headers):
        resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={
                "vehicle_number": "AP-01-CC-SHIP-001",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 3000.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        return resp.json()

    def test_list_shipments(self, client, admin_headers):
        resp = client.get("/api/cold-chain/shipments", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_shipments_unauthenticated(self, client):
        resp = client.get("/api/cold-chain/shipments")
        assert resp.status_code == 401

    def test_create_shipment(self, client, admin_headers, test_vehicle, user_ids):
        driver_id = user_ids["driver"]
        resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": test_vehicle["id"],
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Hyderabad",
                "delivery_address": "Test Market, Hyderabad",
                "product_category": "fish",
                "product_lots": [
                    {"lot_number": "LOT-001", "quantity_kg": 100.0}
                ],
                "total_weight_kg": 100.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
                "notes": "Test shipment",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["origin_city"] == "Nellore"
        assert data["destination_city"] == "Hyderabad"
        assert data["status"] == "scheduled"
        assert "shipment_code" in data

    def test_create_shipment_viewer_forbidden(self, client, viewer_headers, test_vehicle, user_ids):
        driver_id = user_ids["driver"]
        resp = client.post(
            "/api/cold-chain/shipments",
            headers=viewer_headers,
            json={
                "vehicle_id": test_vehicle["id"],
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Hyderabad",
                "delivery_address": "Test Address",
                "product_category": "fish",
                "total_weight_kg": 100.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
            },
        )
        assert resp.status_code == 403

    def test_create_shipment_missing_fields(self, client, admin_headers, test_vehicle):
        resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": test_vehicle["id"],
                "origin_city": "Nellore",
            },
        )
        assert resp.status_code == 422

    def test_dispatch_shipment(self, client, admin_headers, test_vehicle, user_ids):
        driver_id = user_ids["driver"]
        create_resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": test_vehicle["id"],
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Bangalore",
                "delivery_address": "Test Address",
                "product_category": "fish",
                "total_weight_kg": 150.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat(),
            },
        )
        assert create_resp.status_code in (200, 201)
        shipment_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/cold-chain/shipments/{shipment_id}/dispatch",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_get_shipment_detail(self, client, admin_headers, test_vehicle, user_ids):
        driver_id = user_ids["driver"]
        create_resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": test_vehicle["id"],
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Chennai",
                "delivery_address": "Test Address",
                "product_category": "fish",
                "total_weight_kg": 200.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
            },
        )
        assert create_resp.status_code in (200, 201)
        shipment_id = create_resp.json()["id"]

        resp = client.get(
            f"/api/cold-chain/shipments/{shipment_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "shipment" in data
        assert "temperature_logs" in data
        assert "delivery_confirmation" in data
        assert "rejections" in data

    def test_list_shipments_by_status(self, client, admin_headers):
        resp = client.get(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            params={"status": "scheduled"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_shipments_by_city(self, client, admin_headers):
        resp = client.get(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            params={"destination_city": "Hyderabad"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_list_shipments_with_breach(self, client, admin_headers):
        resp = client.get(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            params={"has_breach": False},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestTemperatureLogs:
    @pytest.fixture(scope="class")
    def test_shipment(self, client, admin_headers, user_ids):
        vehicle_resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={
                "vehicle_number": "AP-01-CC-TEMP-001",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 3000.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        vehicle_id = vehicle_resp.json()["id"]
        driver_id = user_ids["driver"]

        resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": vehicle_id,
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Vijayawada",
                "delivery_address": "Test Address",
                "product_category": "fish",
                "total_weight_kg": 250.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
            },
        )
        return resp.json()

    def test_log_temperature(self, client, admin_headers, test_shipment, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=admin_headers,
            json={
                "temperature_c": 2.5,
                "humidity_pct": 85.0,
                "location": "Vehicle Cabin",
                "recorded_by": admin_id,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["temperature_c"] == 2.5
        assert data["humidity_pct"] == 85.0
        assert data["is_breach"] is False

    def test_log_temperature_breach_fish(self, client, admin_headers, test_shipment, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=admin_headers,
            json={
                "temperature_c": 7.0,
                "humidity_pct": 90.0,
                "location": "Vehicle Cabin",
                "recorded_by": admin_id,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["is_breach"] is True
        assert data["breach_threshold_c"] == 4.0

        shipment_check = client.get(
            f"/api/cold-chain/shipments/{test_shipment['id']}",
            headers=admin_headers,
        )
        shipment_data = shipment_check.json()
        assert shipment_data["shipment"]["has_temperature_breach"] is True

    def test_log_temperature_compliant(self, client, admin_headers, test_shipment, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=admin_headers,
            json={
                "temperature_c": 1.0,
                "humidity_pct": 80.0,
                "location": "Vehicle Cabin",
                "recorded_by": admin_id,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["is_breach"] is False

    def test_get_temperature_logs(self, client, admin_headers, test_shipment, user_ids):
        admin_id = user_ids["admin"]
        client.post(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=admin_headers,
            json={
                "temperature_c": 3.0,
                "humidity_pct": 82.0,
                "location": "Vehicle Cabin",
                "recorded_by": admin_id,
            },
        )

        resp = client.get(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_log_temperature_viewer_forbidden(self, client, viewer_headers, test_shipment, user_ids):
        viewer_id = user_ids["viewer"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=viewer_headers,
            json={
                "temperature_c": 2.0,
                "humidity_pct": 80.0,
                "location": "Vehicle",
                "recorded_by": viewer_id,
            },
        )
        assert resp.status_code == 403

    def test_log_temperature_missing_fields(self, client, admin_headers, test_shipment):
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment['id']}/temperature",
            headers=admin_headers,
            json={"temperature_c": 2.0},
        )
        assert resp.status_code == 422


class TestDeliveryConfirmation:
    @pytest.fixture(scope="class")
    def test_shipment_for_delivery(self, client, admin_headers, user_ids):
        vehicle_resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={
                "vehicle_number": "AP-01-CC-DEL-001",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 2000.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        vehicle_id = vehicle_resp.json()["id"]
        driver_id = user_ids["driver"]

        resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": vehicle_id,
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Tirupati",
                "delivery_address": "Test Market",
                "product_category": "fish",
                "total_weight_kg": 300.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            },
        )
        return resp.json()

    def test_confirm_delivery(self, client, admin_headers, test_shipment_for_delivery, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_delivery['id']}/confirm-delivery",
            headers=admin_headers,
            json={
                "recipient_name": "John Market",
                "recipient_phone": "9876543210",
                "photo_url": "https://example.com/photo.jpg",
                "delivered_weight_kg": 300.0,
                "temperature_at_delivery_c": 3.0,
                "notes": "Good condition",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["recipient_name"] == "John Market"
        assert data["is_temperature_compliant"] is True

    def test_confirm_delivery_temp_breach(self, client, admin_headers, test_shipment_for_delivery, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_delivery['id']}/confirm-delivery",
            headers=admin_headers,
            json={
                "recipient_name": "Jane Market",
                "recipient_phone": "9876543211",
                "photo_url": "https://example.com/photo2.jpg",
                "delivered_weight_kg": 300.0,
                "temperature_at_delivery_c": 8.0,
                "notes": "Warm",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["is_temperature_compliant"] is False

    def test_confirm_delivery_viewer_forbidden(self, client, viewer_headers, test_shipment_for_delivery):
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_delivery['id']}/confirm-delivery",
            headers=viewer_headers,
            json={
                "recipient_name": "Test",
                "recipient_phone": "9876543212",
                "photo_url": "https://example.com/photo3.jpg",
                "delivered_weight_kg": 300.0,
                "temperature_at_delivery_c": 2.0,
            },
        )
        assert resp.status_code == 403

    def test_confirm_delivery_missing_fields(self, client, admin_headers, test_shipment_for_delivery):
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_delivery['id']}/confirm-delivery",
            headers=admin_headers,
            json={"recipient_name": "Test"},
        )
        assert resp.status_code == 422


class TestShipmentRejection:
    @pytest.fixture(scope="class")
    def test_shipment_for_rejection(self, client, admin_headers, user_ids):
        vehicle_resp = client.post(
            "/api/cold-chain/vehicles",
            headers=admin_headers,
            json={
                "vehicle_number": "AP-01-CC-REJ-001",
                "vehicle_type": "refrigerated_van",
                "capacity_kg": 2000.0,
                "refrigerated": True,
                "min_temp_c": 0.0,
                "max_temp_c": 4.0,
            },
        )
        vehicle_id = vehicle_resp.json()["id"]
        driver_id = user_ids["driver"]

        resp = client.post(
            "/api/cold-chain/shipments",
            headers=admin_headers,
            json={
                "vehicle_id": vehicle_id,
                "driver_employee_id": driver_id,
                "origin_city": "Nellore",
                "destination_city": "Guntur",
                "delivery_address": "Test Market",
                "product_category": "fish",
                "total_weight_kg": 400.0,
                "required_temp_min_c": 0.0,
                "required_temp_max_c": 4.0,
                "dispatch_time": datetime.now(timezone.utc).isoformat(),
                "eta": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
            },
        )
        return resp.json()

    def test_record_partial_rejection(self, client, admin_headers, test_shipment_for_rejection, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}/reject",
            headers=admin_headers,
            json={
                "rejection_reason": "Quality issue",
                "rejected_quantity_kg": 100.0,
                "accepted_quantity_kg": 300.0,
                "credit_note_number": "CN-001",
                "credit_note_amount": 5000.0,
                "photo_url": "https://example.com/reject.jpg",
                "customer_name": "Market Customer",
                "notes": "Some fish were spoiled",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["rejected_quantity_kg"] == 100.0
        assert data["accepted_quantity_kg"] == 300.0
        assert data["credit_note_amount"] == 5000.0

        shipment_check = client.get(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}",
            headers=admin_headers,
        )
        shipment_data = shipment_check.json()
        assert shipment_data["shipment"]["status"] == "partially_rejected"

    def test_record_full_rejection(self, client, admin_headers, test_shipment_for_rejection, user_ids):
        admin_id = user_ids["admin"]
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}/reject",
            headers=admin_headers,
            json={
                "rejection_reason": "Completely spoiled",
                "rejected_quantity_kg": 400.0,
                "accepted_quantity_kg": 0.0,
                "credit_note_number": "CN-002",
                "credit_note_amount": 20000.0,
                "photo_url": "https://example.com/reject2.jpg",
                "customer_name": "Market Customer 2",
                "notes": "All fish were rotten",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["rejected_quantity_kg"] == 400.0
        assert data["accepted_quantity_kg"] == 0.0

        shipment_check = client.get(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}",
            headers=admin_headers,
        )
        shipment_data = shipment_check.json()
        assert shipment_data["shipment"]["status"] == "fully_rejected"

    def test_record_rejection_viewer_forbidden(self, client, viewer_headers, test_shipment_for_rejection):
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}/reject",
            headers=viewer_headers,
            json={
                "rejection_reason": "Test",
                "rejected_quantity_kg": 50.0,
                "accepted_quantity_kg": 350.0,
                "credit_note_number": "CN-003",
                "credit_note_amount": 2500.0,
            },
        )
        assert resp.status_code == 403

    def test_record_rejection_missing_fields(self, client, admin_headers, test_shipment_for_rejection):
        resp = client.post(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}/reject",
            headers=admin_headers,
            json={
                "rejection_reason": "Test",
            },
        )
        assert resp.status_code == 422

    def test_get_rejection_list(self, client, admin_headers, test_shipment_for_rejection):
        resp = client.get(
            f"/api/cold-chain/shipments/{test_shipment_for_rejection['id']}/rejections",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestColdChainSummary:
    def test_cold_chain_summary(self, client, admin_headers):
        resp = client.get(
            "/api/cold-chain/summary",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "period_days" in data
        assert "total_shipments" in data
        assert "temperature_breach_count" in data
        assert "breach_rate_pct" in data
        assert "rejection_count" in data
        assert "rejection_rate_pct" in data
        assert "by_city" in data
        assert isinstance(data["by_city"], list)

    def test_cold_chain_summary_custom_period(self, client, admin_headers):
        resp = client.get(
            "/api/cold-chain/summary",
            headers=admin_headers,
            params={"days": 7},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["period_days"] == 7

    def test_cold_chain_summary_unauthenticated(self, client):
        resp = client.get("/api/cold-chain/summary")
        assert resp.status_code == 401
