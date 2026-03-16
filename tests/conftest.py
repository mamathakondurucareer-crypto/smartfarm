"""Shared fixtures for all tests — all 10 roles with one test user per role."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from backend.main import app
from backend.database import Base, get_db
from backend.models.user import User, Role
from backend.models.store import StoreConfig, ProductCatalog
from backend.models.supply_chain import StoreStock
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


# ── One test user per role ─────────────────────────────────────────────────────
TEST_USERS = {
    "admin":         {"username": "testadmin",      "password": "testpass123", "role_id": 1},
    "manager":       {"username": "testmanager",    "password": "testpass123", "role_id": 2},
    "supervisor":    {"username": "testsupervisor", "password": "testpass123", "role_id": 3},
    "worker":        {"username": "testworker",     "password": "testpass123", "role_id": 4},
    "viewer":        {"username": "testviewer",     "password": "testpass123", "role_id": 5},
    "store_manager": {"username": "teststoremgr",   "password": "testpass123", "role_id": 6},
    "cashier":       {"username": "testcashier",    "password": "testpass123", "role_id": 7},
    "packer":        {"username": "testpacker",     "password": "testpass123", "role_id": 8},
    "driver":        {"username": "testdriver",     "password": "testpass123", "role_id": 9},
    "scanner":       {"username": "testscanner",    "password": "testpass123", "role_id": 10},
}


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # ── Roles ──────────────────────────────────────────────────────────────────
    roles = [
        Role(id=1,  name="admin",         description="Full system access"),
        Role(id=2,  name="manager",       description="Farm management access"),
        Role(id=3,  name="supervisor",    description="Department supervisor"),
        Role(id=4,  name="worker",        description="Field worker"),
        Role(id=5,  name="viewer",        description="Read-only access"),
        Role(id=6,  name="store_manager", description="Store operations management"),
        Role(id=7,  name="cashier",       description="POS checkout operations"),
        Role(id=8,  name="packer",        description="Packaging and labeling"),
        Role(id=9,  name="driver",        description="Delivery and logistics"),
        Role(id=10, name="scanner",       description="Barcode scanning and stock intake"),
    ]
    db.add_all(roles)
    db.flush()

    # ── One user per role ───────────────────────────────────────────────────────
    for info in TEST_USERS.values():
        user = User(
            username=info["username"],
            email=f"{info['username']}@test.smartfarm.in",
            hashed_password=hash_password(info["password"]),
            full_name=info["username"].title(),
            phone="9000000000",
            role_id=info["role_id"],
        )
        db.add(user)
    db.flush()

    # ── Store config ────────────────────────────────────────────────────────────
    store = StoreConfig(
        store_name="Test SmartFarm Store",
        store_code="TEST-001",
        address="Test Address, Nellore",
        phone="9000000001",
        currency="INR",
        tax_inclusive=False,
        default_payment_mode="cash",
        low_stock_threshold=5,
    )
    db.add(store)
    db.flush()

    # ── Product catalog ─────────────────────────────────────────────────────────
    p1 = ProductCatalog(
        product_code="TEST-FISH-01",
        name="Test Murrel Fish",
        category="fish",
        source_type="farm_produced",
        unit="kg",
        selling_price=300.0,
        mrp=330.0,
        cost_price=180.0,
        gst_rate=5.0,
        is_weighable=True,
        track_expiry=False,
    )
    p2 = ProductCatalog(
        product_code="TEST-EGGS-01",
        name="Test Eggs Tray",
        category="eggs",
        source_type="farm_produced",
        unit="tray",
        selling_price=160.0,
        mrp=180.0,
        cost_price=110.0,
        gst_rate=5.0,
        is_weighable=False,
        track_expiry=False,
    )
    db.add_all([p1, p2])
    db.flush()

    # ── Initial store stock ─────────────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    db.add(StoreStock(
        product_id=p1.id,
        current_qty=100.0,
        reserved_qty=0.0,
        unit="kg",
        avg_cost_per_unit=180.0,
        last_received_at=now,
        updated_at=now,
    ))
    db.add(StoreStock(
        product_id=p2.id,
        current_qty=50.0,
        reserved_qty=0.0,
        unit="tray",
        avg_cost_per_unit=110.0,
        last_received_at=now,
        updated_at=now,
    ))
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


@pytest.fixture()
def db_session():
    """Yields a raw SQLAlchemy session for direct DB manipulation in tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Helper: get token and headers for a given role ─────────────────────────────

def _get_token(client, role: str) -> str:
    info = TEST_USERS[role]
    resp = client.post(
        "/api/auth/login",
        data={"username": info["username"], "password": info["password"]},
    )
    assert resp.status_code == 200, f"Login failed for {role}: {resp.text}"
    return resp.json()["access_token"]


def _headers(client, role: str) -> dict:
    return {"Authorization": f"Bearer {_get_token(client, role)}"}


# ── Backward-compatible admin fixture ──────────────────────────────────────────
@pytest.fixture(scope="session")
def auth_headers(client):
    return _headers(client, "admin")


# ── Per-role header fixtures ───────────────────────────────────────────────────
@pytest.fixture(scope="session")
def admin_headers(client):
    return _headers(client, "admin")

@pytest.fixture(scope="session")
def manager_headers(client):
    return _headers(client, "manager")

@pytest.fixture(scope="session")
def supervisor_headers(client):
    return _headers(client, "supervisor")

@pytest.fixture(scope="session")
def viewer_headers(client):
    return _headers(client, "viewer")

@pytest.fixture(scope="session")
def store_manager_headers(client):
    return _headers(client, "store_manager")

@pytest.fixture(scope="session")
def cashier_headers(client):
    return _headers(client, "cashier")

@pytest.fixture(scope="session")
def packer_headers(client):
    return _headers(client, "packer")

@pytest.fixture(scope="session")
def driver_headers(client):
    return _headers(client, "driver")

@pytest.fixture(scope="session")
def scanner_headers(client):
    return _headers(client, "scanner")


# ── Utility: get user ID for a given role ─────────────────────────────────────
@pytest.fixture(scope="session")
def user_ids(client, admin_headers):
    """Returns {role_name: user_id} for all test users."""
    ids = {}
    for role in TEST_USERS:
        resp = client.get("/api/auth/me", headers=_headers(client, role))
        assert resp.status_code == 200
        ids[role] = resp.json()["id"]
    return ids


# ── Utility: first product from test catalog ──────────────────────────────────
@pytest.fixture(scope="session")
def test_product(client, admin_headers):
    resp = client.get("/api/store/products", headers=admin_headers)
    assert resp.status_code == 200
    products = resp.json()
    products = products if isinstance(products, list) else products.get("products", [])
    return products[0]


@pytest.fixture(scope="session")
def test_products(client, admin_headers):
    resp = client.get("/api/store/products", headers=admin_headers)
    assert resp.status_code == 200
    products = resp.json()
    return products if isinstance(products, list) else products.get("products", [])
