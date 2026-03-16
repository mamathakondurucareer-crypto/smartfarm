"""Functional tests for Supply Chain Transfer endpoints."""

import pytest
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════
# SUPPLY CHAIN TRANSFERS
# ═══════════════════════════════════════════════════════════════
class TestSupplyChainTransfers:
    def test_list_transfers(self, client, admin_headers):
        resp = client.get("/api/supply-chain/transfers", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        transfers = data if isinstance(data, list) else data.get("transfers", [])
        assert isinstance(transfers, list)

    def test_list_transfers_unauthenticated(self, client):
        resp = client.get("/api/supply-chain/transfers")
        assert resp.status_code == 401

    def test_create_transfer(self, client, admin_headers, test_product):
        resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "source_id": 1,
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 20.0,
                "unit": "kg",
                "quality_grade": "A",
                "cost_per_unit": 180.0,
                "notes": "Test transfer from fish pond",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "transfer_code" in data
        assert data["status"] == "in_transit"
        assert data["product_name"] == test_product["name"]
        assert data["quantity_transferred"] == 20.0

    def test_create_transfer_poultry(self, client, admin_headers, test_product):
        resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "poultry",
                "product_id": test_product["id"],
                "product_name": "Fresh Eggs",
                "quantity_transferred": 10.0,
                "unit": "tray",
                "quality_grade": "A",
                "cost_per_unit": 120.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["source_type"] == "poultry"

    def test_create_transfer_missing_required_fields(self, client, admin_headers):
        resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "source_type": "aquaculture",
                # Missing product_id, product_name, quantity_transferred, unit, transfer_date
            },
        )
        assert resp.status_code == 422

    def test_create_transfer_viewer_forbidden(self, client, viewer_headers, test_product):
        resp = client.post(
            "/api/supply-chain/transfers",
            headers=viewer_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 5.0,
                "unit": "kg",
                "quality_grade": "A",
                "cost_per_unit": 150.0,
            },
        )
        assert resp.status_code == 403

    def test_get_transfer_by_id(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "crops",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 15.0,
                "unit": "kg",
                "quality_grade": "B",
                "cost_per_unit": 40.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        transfer_id = create_resp.json()["id"]

        get_resp = client.get(
            f"/api/supply-chain/transfers/{transfer_id}",
            headers=admin_headers,
        )
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == transfer_id

    def test_get_transfer_not_found(self, client, admin_headers):
        resp = client.get("/api/supply-chain/transfers/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_receive_transfer(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 25.0,
                "unit": "kg",
                "quality_grade": "A",
                "cost_per_unit": 180.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        transfer_id = create_resp.json()["id"]

        receive_resp = client.put(
            f"/api/supply-chain/transfers/{transfer_id}/receive",
            headers=admin_headers,
            json={"received_qty": 24.5, "notes": "Slight shortage on delivery"},
        )
        assert receive_resp.status_code == 200
        data = receive_resp.json()
        assert data["status"] == "received"

    def test_receive_transfer_full_qty(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 10.0,
                "unit": "kg",
                "quality_grade": "A",
                "cost_per_unit": 180.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        transfer_id = create_resp.json()["id"]

        receive_resp = client.put(
            f"/api/supply-chain/transfers/{transfer_id}/receive",
            headers=admin_headers,
            json={},  # No qty provided — should use full quantity_transferred
        )
        assert receive_resp.status_code == 200
        data = receive_resp.json()
        assert data["status"] == "received"

    def test_reject_transfer(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 5.0,
                "unit": "kg",
                "quality_grade": "C",
                "cost_per_unit": 100.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        transfer_id = create_resp.json()["id"]

        reject_resp = client.put(
            f"/api/supply-chain/transfers/{transfer_id}/reject",
            headers=admin_headers,
            json={"rejection_reason": "Poor quality — grade C not acceptable"},
        )
        assert reject_resp.status_code == 200
        data = reject_resp.json()
        assert data["status"] == "rejected"
        assert "rejection_reason" in data

    def test_reject_transfer_missing_reason(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 3.0,
                "unit": "kg",
                "quality_grade": "A",
                "cost_per_unit": 150.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        transfer_id = create_resp.json()["id"]

        reject_resp = client.put(
            f"/api/supply-chain/transfers/{transfer_id}/reject",
            headers=admin_headers,
            json={},  # Missing rejection_reason
        )
        assert reject_resp.status_code == 422

    def test_cannot_receive_already_received(self, client, admin_headers, test_product):
        create_resp = client.post(
            "/api/supply-chain/transfers",
            headers=admin_headers,
            json={
                "transfer_date": _now_iso(),
                "source_type": "aquaculture",
                "product_id": test_product["id"],
                "product_name": test_product["name"],
                "quantity_transferred": 8.0,
                "unit": "kg",
                "quality_grade": "A",
                "cost_per_unit": 160.0,
            },
        )
        assert create_resp.status_code in (200, 201)
        transfer_id = create_resp.json()["id"]

        # Receive once
        client.put(
            f"/api/supply-chain/transfers/{transfer_id}/receive",
            headers=admin_headers,
            json={},
        )
        # Try to receive again
        re_recv = client.put(
            f"/api/supply-chain/transfers/{transfer_id}/receive",
            headers=admin_headers,
            json={},
        )
        assert re_recv.status_code == 400

    def test_filter_transfers_by_status(self, client, admin_headers):
        resp = client.get(
            "/api/supply-chain/transfers?status=pending",
            headers=admin_headers,
        )
        assert resp.status_code == 200
