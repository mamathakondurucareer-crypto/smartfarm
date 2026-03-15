"""Barcode generation, registration, and resolution service."""
import hashlib
import time
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.packing import BarcodeRegistry
from backend.models.store import ProductCatalog


def generate_barcode(product_id: int, prefix: str = "SFN") -> str:
    """Generate a unique barcode string."""
    ts = str(int(time.time() * 1000))[-8:]
    checksum = hashlib.md5(f"{product_id}{ts}".encode()).hexdigest()[:4].upper()
    return f"{prefix}{product_id:04d}{ts}{checksum}"


def register_barcode(
    db: Session,
    barcode: str,
    entity_type: str,
    entity_id: int,
    product_id: int,
    user_id: int,
) -> BarcodeRegistry:
    """Register a barcode in the registry.  Returns existing record if already registered."""
    existing = db.query(BarcodeRegistry).filter(BarcodeRegistry.barcode == barcode).first()
    if existing:
        return existing
    entry = BarcodeRegistry(
        barcode=barcode,
        entity_type=entity_type,
        entity_id=entity_id,
        product_id=product_id,
        generated_at=datetime.now(timezone.utc),
        generated_by=user_id,
    )
    db.add(entry)
    return entry


def resolve_barcode(db: Session, barcode: str) -> Optional[dict]:
    """Resolve a barcode to its entity.

    Checks the product_catalog barcode column first, then the barcode registry.
    Returns a dict with entity info or None if not found.
    """
    # 1. Check product catalog direct barcode
    product = db.query(ProductCatalog).filter(ProductCatalog.barcode == barcode).first()
    if product:
        return {
            "type": "product",
            "product_id": product.id,
            "name": product.name,
            "unit": product.unit,
            "selling_price": product.selling_price,
            "gst_rate": product.gst_rate,
        }

    # 2. Check barcode registry
    entry = (
        db.query(BarcodeRegistry)
        .filter(BarcodeRegistry.barcode == barcode, BarcodeRegistry.is_active.is_(True))
        .first()
    )
    if entry:
        entry.last_scanned_at = datetime.now(timezone.utc)
        entry.scan_count += 1
        return {
            "type": entry.entity_type,
            "entity_id": entry.entity_id,
            "product_id": entry.product_id,
        }

    return None
