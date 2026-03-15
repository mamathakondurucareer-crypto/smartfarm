"""Functional tests for health/info endpoints."""


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_status_is_healthy(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_has_app_name(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert "app" in data
        assert "SmartFarm" in data["app"]


class TestInfoEndpoint:
    def test_info_returns_200(self, client):
        resp = client.get("/api/info")
        assert resp.status_code == 200

    def test_info_has_farm_details(self, client):
        resp = client.get("/api/info")
        data = resp.json()
        assert "farm" in data
        assert "name" in data["farm"]
        assert "location" in data["farm"]

    def test_info_has_modules(self, client):
        resp = client.get("/api/info")
        data = resp.json()
        assert "modules" in data
        assert isinstance(data["modules"], list)
        assert len(data["modules"]) > 0

    def test_info_has_version(self, client):
        resp = client.get("/api/info")
        data = resp.json()
        assert "version" in data


class TestDocsEndpoint:
    def test_swagger_docs_accessible(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json_accessible(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert "info" in data
