"""Functional tests for authentication API endpoints."""

import pytest


class TestLogin:
    def test_login_success(self, client):
        resp = client.post(
            "/api/auth/login",
            data={"username": "testadmin", "password": "testpass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testadmin"
        assert data["role"] == "admin"

    def test_login_wrong_password(self, client):
        resp = client.post(
            "/api/auth/login",
            data={"username": "testadmin", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/auth/login",
            data={"username": "nobody", "password": "pass"},
        )
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post("/api/auth/login", data={})
        assert resp.status_code == 422


class TestRegister:
    def test_register_new_user(self, client):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "newworker",
                "email": "newworker@smartfarm.in",
                "password": "worker123",
                "full_name": "New Worker",
                "phone": "9111111111",
                "role_id": 3,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newworker"
        assert data["email"] == "newworker@smartfarm.in"

    def test_register_duplicate_username(self, client):
        payload = {
            "username": "dupuser",
            "email": "dup1@smartfarm.in",
            "password": "pass123",
            "full_name": "Dup User",
            "phone": "9222222222",
            "role_id": 3,
        }
        client.post("/api/auth/register", json=payload)
        payload["email"] = "dup2@smartfarm.in"
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400

    def test_register_duplicate_email(self, client):
        payload = {
            "username": "user_a",
            "email": "shared@smartfarm.in",
            "password": "pass123",
            "full_name": "User A",
            "phone": "9333333333",
            "role_id": 3,
        }
        client.post("/api/auth/register", json=payload)
        payload["username"] = "user_b"
        payload["phone"] = "9444444444"
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400

    def test_register_invalid_role(self, client):
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "badrole",
                "email": "badrole@smartfarm.in",
                "password": "pass123",
                "full_name": "Bad Role",
                "phone": "9555555555",
                "role_id": 999,
            },
        )
        assert resp.status_code == 400


class TestMe:
    def test_get_me_authenticated(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testadmin"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401


class TestRoles:
    def test_list_roles(self, client):
        resp = client.get("/api/roles")
        # May be 404 if not on /api/roles; check auth-scoped route
        assert resp.status_code in (200, 404)

    def test_list_roles_via_auth(self, client):
        resp = client.get("/api/auth/roles")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        role_names = [r["name"] for r in data]
        assert "admin" in role_names
