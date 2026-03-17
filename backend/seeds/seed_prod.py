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
from backend.services.auth_service import hash_password


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
        ))
        print(f"  Created admin user: {admin_username}")
    else:
        print(f"  Admin user already exists: {admin_username} — skipping.")

    db.commit()
    print("Production seed complete.")


if __name__ == "__main__":
    seed()
