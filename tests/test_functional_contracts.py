"""Functional tests for Contract Farming & Consulting endpoints."""

import pytest
from datetime import date, timedelta


class TestNeighbouringFarms:
    def test_create_farm(self, client, admin_headers):
        resp = client.post(
            "/api/contracts/farms",
            headers=admin_headers,
            json={
                "farm_name": "Raju's Organic Farm",
                "owner_name": "Raju Reddy",
                "contact_phone": "9876543210",
                "village": "Kovur",
                "district": "SPSR Nellore",
                "land_acres": 8.5,
                "current_crops": "Turmeric, Groundnut",
                "notes": "Experienced organic farmer",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["farm_name"] == "Raju's Organic Farm"
        assert data["owner_name"] == "Raju Reddy"
        return data["id"]

    def test_create_farm_viewer_forbidden(self, client, viewer_headers):
        resp = client.post(
            "/api/contracts/farms",
            headers=viewer_headers,
            json={
                "farm_name": "Forbidden Farm",
                "owner_name": "Nobody",
                "contact_phone": "1111111111",
            },
        )
        assert resp.status_code == 403

    def test_list_farms(self, client, admin_headers):
        resp = client.get("/api/contracts/farms", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestConsultingContracts:
    def _create_farm_id(self, client, headers):
        r = client.post(
            "/api/contracts/farms",
            headers=headers,
            json={
                "farm_name": "Contract Test Farm",
                "owner_name": "Test Owner",
                "contact_phone": "9000000001",
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_contract(self, client, admin_headers):
        farm_id = self._create_farm_id(client, admin_headers)
        resp = client.post(
            "/api/contracts/",
            headers=admin_headers,
            json={
                "contract_number": "CON-2025-001",
                "neighbouring_farm_id": farm_id,
                "client_name": "Raju Reddy",
                "contract_type": "aquaculture_consulting",
                "scope": "Pond management, feed optimisation, disease prevention",
                "start_date": str(date.today()),
                "end_date": str(date.today() + timedelta(days=365)),
                "contract_value": 120000.0,
                "payment_terms": "Monthly",
                "status": "active",
                "notes": "1-year consulting engagement",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["contract_number"] == "CON-2025-001"
        assert data["contract_value"] == 120000.0
        return data["id"]

    def test_list_contracts(self, client, admin_headers):
        resp = client.get("/api/contracts/", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_contract_by_id(self, client, admin_headers):
        farm_id = self._create_farm_id(client, admin_headers)
        r = client.post(
            "/api/contracts/",
            headers=admin_headers,
            json={
                "contract_number": "CON-GET-001",
                "client_name": "Get Test Client",
                "contract_type": "feed_consulting",
                "start_date": str(date.today()),
                "contract_value": 50000.0,
            },
        )
        assert r.status_code in (200, 201)
        contract_id = r.json()["id"]

        resp = client.get(f"/api/contracts/{contract_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == contract_id

    def test_update_contract_status(self, client, admin_headers):
        farm_id = self._create_farm_id(client, admin_headers)
        r = client.post(
            "/api/contracts/",
            headers=admin_headers,
            json={
                "contract_number": "CON-STATUS-001",
                "client_name": "Status Test Client",
                "contract_type": "training",
                "start_date": str(date.today() - timedelta(days=365)),
                "end_date": str(date.today()),
                "contract_value": 30000.0,
            },
        )
        assert r.status_code in (200, 201)
        contract_id = r.json()["id"]

        resp = client.put(
            f"/api/contracts/{contract_id}/status",
            headers=admin_headers,
            params={"status": "completed"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"


class TestServiceDeliveryLogs:
    def _create_contract_id(self, client, headers, suffix="SL1"):
        r = client.post(
            "/api/contracts/",
            headers=headers,
            json={
                "contract_number": f"SVC-{suffix}",
                "client_name": "Service Log Client",
                "contract_type": "pond_management",
                "start_date": str(date.today()),
                "contract_value": 60000.0,
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_service_log(self, client, admin_headers):
        contract_id = self._create_contract_id(client, admin_headers, "SL1")
        resp = client.post(
            "/api/contracts/service-logs",
            headers=admin_headers,
            json={
                "contract_id": contract_id,
                "service_date": str(date.today()),
                "service_type": "pond_inspection",
                "description": "Monthly water quality check and pond cleaning",
                "hours_spent": 6.0,
                "materials_cost": 500.0,
                "service_charge": 2500.0,
                "outcome": "Water parameters normal, minor algae growth removed",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["service_type"] == "pond_inspection"

    def test_list_service_logs_by_contract(self, client, admin_headers):
        contract_id = self._create_contract_id(client, admin_headers, "SL2")
        resp = client.get(
            f"/api/contracts/service-logs/{contract_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestConsultingInvoices:
    def _create_contract_id(self, client, headers, suffix="INV1"):
        r = client.post(
            "/api/contracts/",
            headers=headers,
            json={
                "contract_number": f"INV-CON-{suffix}",
                "client_name": "Invoice Client",
                "contract_type": "aquaculture_consulting",
                "start_date": str(date.today()),
                "contract_value": 120000.0,
            },
        )
        assert r.status_code in (200, 201)
        return r.json()["id"]

    def test_create_invoice(self, client, admin_headers):
        contract_id = self._create_contract_id(client, admin_headers, "INV1")
        resp = client.post(
            "/api/contracts/invoices",
            headers=admin_headers,
            json={
                "invoice_number": "INV-2025-001",
                "contract_id": contract_id,
                "invoice_date": str(date.today()),
                "due_date": str(date.today() + timedelta(days=30)),
                "amount": 10000.0,
                "tax_amount": 1800.0,
                "total_amount": 11800.0,
                "description": "Monthly consulting fee — June 2025",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["invoice_number"] == "INV-2025-001"
        assert data["total_amount"] == 11800.0
        return data["id"]

    def test_list_invoices_by_contract(self, client, admin_headers):
        contract_id = self._create_contract_id(client, admin_headers, "INV2")
        resp = client.get(
            f"/api/contracts/invoices/{contract_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_mark_invoice_paid(self, client, admin_headers):
        contract_id = self._create_contract_id(client, admin_headers, "INV3")
        r = client.post(
            "/api/contracts/invoices",
            headers=admin_headers,
            json={
                "invoice_number": "INV-PAY-001",
                "contract_id": contract_id,
                "invoice_date": str(date.today()),
                "amount": 10000.0,
                "tax_amount": 1800.0,
                "total_amount": 11800.0,
            },
        )
        assert r.status_code in (200, 201)
        invoice_id = r.json()["id"]

        resp = client.patch(
            f"/api/contracts/invoices/{invoice_id}/pay",
            headers=admin_headers,
            params={"amount": 11800.0, "payment_mode": "bank_transfer"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("paid", "partial")

    def test_analytics_revenue(self, client, admin_headers):
        resp = client.get("/api/contracts/analytics/revenue", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (dict, list))
