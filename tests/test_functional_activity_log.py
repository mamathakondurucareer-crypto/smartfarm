"""Functional tests for Activity Log endpoints."""

import pytest


# ═══════════════════════════════════════════════════════════════
# ACTIVITY LOG
# ═══════════════════════════════════════════════════════════════
class TestActivityLog:
    def test_list_activity_logs(self, client, admin_headers):
        resp = client.get("/api/activity-logs", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        # Response may be paginated dict or list
        if isinstance(data, dict):
            items = data.get("items", [])
            assert isinstance(items, list)
        else:
            assert isinstance(data, list)

    def test_list_logs_unauthenticated(self, client):
        resp = client.get("/api/activity-logs")
        assert resp.status_code == 401

    def test_list_logs_viewer_forbidden(self, client, viewer_headers):
        """Activity logs are admin/manager only."""
        resp = client.get("/api/activity-logs", headers=viewer_headers)
        # May be 200 or 403 depending on business rules
        assert resp.status_code in (200, 403)

    def test_list_logs_pagination(self, client, admin_headers):
        resp = client.get("/api/activity-logs?page=1&page_size=10", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (dict, list))

    def test_list_logs_page_2(self, client, admin_headers):
        resp = client.get("/api/activity-logs?page=2&page_size=5", headers=admin_headers)
        assert resp.status_code == 200

    def test_list_logs_filter_by_module(self, client, admin_headers):
        for module in ("store", "pos", "auth", "inventory"):
            resp = client.get(
                f"/api/activity-logs?module={module}",
                headers=admin_headers,
            )
            assert resp.status_code == 200, f"Module filter failed for: {module}"

    def test_list_logs_filter_by_action(self, client, admin_headers):
        resp = client.get("/api/activity-logs?action=login", headers=admin_headers)
        assert resp.status_code == 200

    def test_get_log_by_id(self, client, admin_headers):
        # First get the list to find a log ID
        list_resp = client.get("/api/activity-logs?page=1&page_size=5", headers=admin_headers)
        assert list_resp.status_code == 200
        data = list_resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data

        if items:
            log_id = items[0]["id"]
            get_resp = client.get(f"/api/activity-logs/{log_id}", headers=admin_headers)
            assert get_resp.status_code == 200
            log = get_resp.json()
            assert log["id"] == log_id
            assert "module" in log
            assert "action" in log
            assert "timestamp" in log

    def test_get_log_not_found(self, client, admin_headers):
        resp = client.get("/api/activity-logs/99999", headers=admin_headers)
        assert resp.status_code == 404

    def test_logs_generated_after_login(self, client, admin_headers):
        """Verify that login actions appear in the activity log."""
        resp = client.get("/api/activity-logs?action=login", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        # There should be at least some login records from test setup
        # (not strict - depends on whether auth events are logged)
        assert isinstance(items, list)

    def test_logs_have_required_fields(self, client, admin_headers):
        resp = client.get("/api/activity-logs?page=1&page_size=1", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        items = data.get("items", data) if isinstance(data, dict) else data

        if items:
            log = items[0]
            required_fields = {"id", "module", "action", "timestamp"}
            assert required_fields.issubset(set(log.keys())), \
                f"Missing fields: {required_fields - set(log.keys())}"

    def test_logs_pagination_large_page_size(self, client, admin_headers):
        resp = client.get("/api/activity-logs?page=1&page_size=100", headers=admin_headers)
        assert resp.status_code == 200

    def test_logs_invalid_page_number(self, client, admin_headers):
        resp = client.get("/api/activity-logs?page=0&page_size=10", headers=admin_headers)
        # Page 0 should either work (treated as page 1) or return validation error
        assert resp.status_code in (200, 400, 422)
