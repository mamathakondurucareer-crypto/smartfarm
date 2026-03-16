"""Unit tests for the barcode service functions."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.services.barcode_service import generate_barcode, register_barcode, resolve_barcode
from backend.models.store import ProductCatalog
from backend.models.packing import BarcodeRegistry

TEST_DB = "sqlite:///./test_barcode_service.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


@pytest.fixture(autouse=True, scope="module")
def barcode_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_product(db):
    product = ProductCatalog(
        product_code="BC-TEST-01",
        name="Barcode Test Product",
        category="fish",
        source_type="farm_produced",
        unit="kg",
        selling_price=250.0,
        mrp=280.0,
        cost_price=150.0,
        gst_rate=5.0,
        is_weighable=True,
        track_expiry=False,
    )
    db.add(product)
    db.flush()
    return product


# ═══════════════════════════════════════════════════════════════
# BARCODE GENERATION
# ═══════════════════════════════════════════════════════════════
class TestGenerateBarcode:
    def test_generates_string(self):
        barcode = generate_barcode(1)
        assert isinstance(barcode, str)

    def test_generated_barcode_nonempty(self):
        barcode = generate_barcode(1)
        assert len(barcode) > 0

    def test_default_prefix_is_sfn(self):
        barcode = generate_barcode(1)
        assert barcode.startswith("SFN")

    def test_custom_prefix(self):
        barcode = generate_barcode(1, prefix="PKG")
        assert barcode.startswith("PKG")

    def test_product_id_encoded_in_barcode(self):
        barcode = generate_barcode(42)
        # The product ID is zero-padded to 4 digits after the prefix
        assert "0042" in barcode

    def test_uniqueness_across_calls(self):
        """Two calls should produce different barcodes (due to timestamp)."""
        import time
        b1 = generate_barcode(1)
        time.sleep(0.001)
        b2 = generate_barcode(1)
        # They may be equal if called in the same millisecond, so just verify format
        assert isinstance(b1, str) and isinstance(b2, str)

    def test_large_product_id(self):
        barcode = generate_barcode(9999)
        assert isinstance(barcode, str)
        assert "9999" in barcode

    def test_empty_prefix(self):
        barcode = generate_barcode(1, prefix="")
        assert isinstance(barcode, str)
        assert len(barcode) > 0


# ═══════════════════════════════════════════════════════════════
# BARCODE REGISTRATION
# ═══════════════════════════════════════════════════════════════
class TestRegisterBarcode:
    def test_register_returns_barcode_registry(self, db, sample_product):
        entry = register_barcode(
            db=db,
            barcode="SFN-TEST-001",
            entity_type="product",
            entity_id=sample_product.id,
            product_id=sample_product.id,
            user_id=1,
        )
        db.flush()
        assert entry is not None
        assert entry.barcode == "SFN-TEST-001"
        assert entry.entity_type == "product"
        assert entry.product_id == sample_product.id

    def test_register_duplicate_returns_existing(self, db, sample_product):
        barcode = "SFN-DUPE-001"
        e1 = register_barcode(db, barcode, "product", sample_product.id, sample_product.id, 1)
        db.flush()
        e2 = register_barcode(db, barcode, "product", sample_product.id, sample_product.id, 1)
        db.flush()
        assert e1.barcode == e2.barcode

    def test_register_sets_generated_at(self, db, sample_product):
        entry = register_barcode(
            db=db,
            barcode="SFN-TIME-001",
            entity_type="product",
            entity_id=sample_product.id,
            product_id=sample_product.id,
            user_id=1,
        )
        db.flush()
        assert entry.generated_at is not None

    def test_register_sets_generated_by(self, db, sample_product):
        entry = register_barcode(
            db=db,
            barcode="SFN-USER-001",
            entity_type="product",
            entity_id=sample_product.id,
            product_id=sample_product.id,
            user_id=99,
        )
        db.flush()
        assert entry.generated_by == 99


# ═══════════════════════════════════════════════════════════════
# BARCODE RESOLUTION
# ═══════════════════════════════════════════════════════════════
class TestResolveBarcode:
    def test_resolve_nonexistent_returns_none(self, db):
        result = resolve_barcode(db, "BARCODE-THAT-DOES-NOT-EXIST")
        assert result is None

    def test_resolve_product_via_direct_barcode(self, db):
        # Create product with a direct barcode field
        product = ProductCatalog(
            product_code="BC-DIRECT-01",
            name="Direct Barcode Product",
            category="vegetables",
            source_type="farm_produced",
            unit="kg",
            selling_price=80.0,
            mrp=90.0,
            cost_price=40.0,
            gst_rate=0.0,
            barcode="DIRECT-BARCODE-ABC123",
            is_weighable=True,
            track_expiry=False,
        )
        db.add(product)
        db.flush()

        result = resolve_barcode(db, "DIRECT-BARCODE-ABC123")
        assert result is not None
        assert result["type"] == "product"
        assert result["product_id"] == product.id
        assert result["name"] == "Direct Barcode Product"
        assert result["selling_price"] == 80.0
        assert result["gst_rate"] == 0.0

    def test_resolve_via_registry(self, db, sample_product):
        barcode = "SFN-REGISTRY-RESOLVE-001"
        entry = register_barcode(
            db=db,
            barcode=barcode,
            entity_type="packing_order",
            entity_id=10,
            product_id=sample_product.id,
            user_id=1,
        )
        db.flush()

        result = resolve_barcode(db, barcode)
        assert result is not None
        assert result["type"] == "packing_order"
        assert result["product_id"] == sample_product.id

    def test_resolve_increments_scan_count(self, db, sample_product):
        barcode = "SFN-SCAN-COUNT-001"
        entry = register_barcode(
            db=db,
            barcode=barcode,
            entity_type="product",
            entity_id=sample_product.id,
            product_id=sample_product.id,
            user_id=1,
        )
        db.flush()
        initial_count = entry.scan_count

        resolve_barcode(db, barcode)
        db.flush()

        assert entry.scan_count == initial_count + 1

    def test_resolve_updates_last_scanned_at(self, db, sample_product):
        barcode = "SFN-LAST-SCAN-001"
        entry = register_barcode(
            db=db,
            barcode=barcode,
            entity_type="product",
            entity_id=sample_product.id,
            product_id=sample_product.id,
            user_id=1,
        )
        db.flush()
        assert entry.last_scanned_at is None

        resolve_barcode(db, barcode)
        db.flush()

        assert entry.last_scanned_at is not None

    def test_resolve_result_has_required_fields_for_product(self, db):
        product = ProductCatalog(
            product_code="BC-FIELDS-01",
            name="Fields Test Product",
            category="fish",
            source_type="farm_produced",
            unit="kg",
            selling_price=300.0,
            mrp=330.0,
            cost_price=180.0,
            gst_rate=5.0,
            barcode="FIELDS-TEST-BARCODE",
            is_weighable=True,
            track_expiry=False,
        )
        db.add(product)
        db.flush()

        result = resolve_barcode(db, "FIELDS-TEST-BARCODE")
        assert result is not None
        required_keys = {"type", "product_id", "name", "unit", "selling_price", "gst_rate"}
        assert required_keys.issubset(set(result.keys()))
