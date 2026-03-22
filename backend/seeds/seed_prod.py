"""
Production seed — creates ONLY the minimum required data:
  • All 10 roles
  • 1 admin user  (credentials read from ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD env vars)

Existing data is never overwritten — safe to re-run.

Usage:
  ADMIN_PASSWORD=<strong> python -m backend.seeds.seed_prod
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import init_db, SessionLocal
from backend.models import Role, User
from backend.models.sensor import SensorDevice
from backend.services.auth_service import hash_password


# id, device_id, name, sensor_type, location, zone, protocol
SENSOR_DEVICES = [
    (1,  "SFDEV-WQ-P1",     "Pond P1 Water Quality",  "water_quality", "Pond P1",        "pond_p1",      "lorawan"),
    (2,  "SFDEV-WQ-P2",     "Pond P2 Water Quality",  "water_quality", "Pond P2",        "pond_p2",      "lorawan"),
    (3,  "SFDEV-WQ-P3",     "Pond P3 Water Quality",  "water_quality", "Pond P3",        "pond_p3",      "lorawan"),
    (4,  "SFDEV-WQ-P4",     "Pond P4 Water Quality",  "water_quality", "Pond P4",        "pond_p4",      "lorawan"),
    (5,  "SFDEV-WQ-P5",     "Pond P5 Water Quality",  "water_quality", "Pond P5",        "pond_p5",      "lorawan"),
    (6,  "SFDEV-WQ-P6",     "Pond P6 Water Quality",  "water_quality", "Pond P6",        "pond_p6",      "lorawan"),
    (7,  "SFDEV-ENV-MAIN",  "Main Weather Station",   "weather",       "Farm Perimeter", "weather",      "wifi"),
    (8,  "SFDEV-GH1",       "Greenhouse 1 Climate",   "environmental", "Greenhouse 1",   "greenhouse",   "wifi"),
    (9,  "SFDEV-GH2",       "Greenhouse 2 Climate",   "environmental", "Greenhouse 2",   "greenhouse",   "wifi"),
    (10, "SFDEV-VF",        "Vertical Farm Climate",  "environmental", "Vertical Farm",  "vertical_farm","wifi"),
    (11, "SFDEV-ENERGY",    "Solar Energy Meter",     "level",         "Solar Array",    "energy",       "modbus"),
    (12, "SFDEV-RESERVOIR", "Reservoir Level Sensor", "level",         "Reservoir",      "reservoir",    "lorawan"),
    (13, "SFDEV-POULTRY",   "Poultry House Sensor",   "environmental", "Poultry House",  "poultry",      "wifi"),
    (14, "SFDEV-SOIL",      "Field Soil Sensor",      "soil",          "Field Crops",    "field",        "lorawan"),
]

ROLES = [
    (1,  "admin",         "Full system access"),
    (2,  "manager",       "Farm management access"),
    (3,  "supervisor",    "Department supervisor"),
    (4,  "worker",        "Field worker"),
    (5,  "viewer",        "Read-only access"),
    (6,  "store_manager", "Store operations management"),
    (7,  "cashier",       "POS checkout operations"),
    (8,  "packer",        "Packaging and labeling"),
    (9,  "driver",        "Delivery and logistics"),
    (10, "scanner",       "Barcode scanning and stock intake"),
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()


def _seed(db) -> None:
    # ── Roles ────────────────────────────────────────────────────────────────
    for rid, name, desc in ROLES:
        if not db.query(Role).filter_by(name=name).first():
            db.add(Role(id=rid, name=name, description=desc))
    db.flush()

    admin_role = db.query(Role).filter_by(name="admin").first()

    # ── Admin user ────────────────────────────────────────────────────────────
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    admin_email    = os.getenv("ADMIN_EMAIL", "admin@smartfarm.in")

    if not admin_password:
        print(
            "ERROR: ADMIN_PASSWORD environment variable is required for the production seed.\n"
            "  Set it before running:  ADMIN_PASSWORD=<strong_password> python -m backend.seeds.seed_prod",
            file=sys.stderr,
        )
        sys.exit(1)

    existing = db.query(User).filter_by(username=admin_username).first()
    if not existing:
        db.add(User(
            username=admin_username,
            email=admin_email,
            hashed_password=hash_password(admin_password),
            full_name="Farm Administrator",
            role_id=admin_role.id,
            must_change_password=True,
        ))
        print(f"  Created admin user: {admin_username} (must change password on first login)")
    else:
        print(f"  Admin user already exists: {admin_username} — skipping.")

    # ── Sensor devices ───────────────────────────────────────────────────────
    for sid, device_id, name, sensor_type, location, zone, protocol in SENSOR_DEVICES:
        if not db.query(SensorDevice).filter_by(device_id=device_id).first():
            db.add(SensorDevice(
                id=sid, device_id=device_id, name=name,
                sensor_type=sensor_type, location=location,
                zone=zone, protocol=protocol, status="online",
            ))
            print(f"  Registered sensor device: {device_id} ({name})")
        else:
            print(f"  Sensor device already exists: {device_id} — skipping.")

    db.commit()
    print("Production seed complete.")


if __name__ == "__main__":
    seed()
