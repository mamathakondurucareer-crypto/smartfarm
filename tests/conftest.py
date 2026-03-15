"""Shared fixtures for all tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.models.user import User, Role
from backend.services.auth_service import hash_password

TEST_DATABASE_URL = "sqlite:///./test_smartfarm.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed roles
    roles = [
        Role(id=1, name="admin", description="Full system access"),
        Role(id=2, name="manager", description="Farm management access"),
        Role(id=3, name="viewer", description="Read-only access"),
    ]
    db.add_all(roles)
    db.flush()
    # Seed admin user
    admin = User(
        username="testadmin",
        email="testadmin@smartfarm.in",
        hashed_password=hash_password("testpass123"),
        full_name="Test Admin",
        phone="9000000000",
        role_id=1,
    )
    db.add(admin)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def auth_headers(client):
    resp = client.post(
        "/api/auth/login",
        data={"username": "testadmin", "password": "testpass123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
