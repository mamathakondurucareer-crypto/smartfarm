"""Store configuration, product catalog, and pricing rules router."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.store import StoreConfig, ProductCatalog, PriceRule
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.barcode_service import generate_barcode, register_barcode
from backend.schemas import (
    StoreConfigOut, StoreConfigUpdate,
    ProductCatalogCreate, ProductCatalogOut, ProductCatalogUpdate,
    PriceRuleCreate, PriceRuleOut,
    BarcodeGenerateRequest, BarcodeOut,
)

router = APIRouter(prefix="/api/store", tags=["Store — Config & Catalog"])

ADMIN_ROLES = ("admin", "store_manager")


# ═══════════════════════════════════════════════════════════════
# STORE CONFIG
# ═══════════════════════════════════════════════════════════════

@router.get("/config", response_model=StoreConfigOut)
def get_store_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the store config, creating a default entry if none exists."""
    cfg = db.query(StoreConfig).first()
    if not cfg:
        cfg = StoreConfig(
            store_name="SmartFarm Store",
            store_code="SFN-001",
            currency="INR",
            tax_inclusive=False,
            default_payment_mode="cash",
            low_stock_threshold=10,
        )
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


@router.put("/config", response_model=StoreConfigOut)
def update_store_config(
    data: StoreConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    cfg = db.query(StoreConfig).first()
    if not cfg:
        cfg = StoreConfig(store_code="SFN-001")
        db.add(cfg)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(cfg, field, value)
    db.commit()
    db.refresh(cfg)
    return cfg


# ═══════════════════════════════════════════════════════════════
# PRODUCT CATALOG
# ═══════════════════════════════════════════════════════════════

@router.get("/products", response_model=List[ProductCatalogOut])
def list_products(
    is_active: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ProductCatalog)
    if is_active is not None:
        q = q.filter(ProductCatalog.is_active == is_active)
    if category:
        q = q.filter(ProductCatalog.category == category)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            ProductCatalog.name.ilike(pattern)
            | ProductCatalog.product_code.ilike(pattern)
        )
    return q.order_by(ProductCatalog.name).all()


@router.post("/products", response_model=ProductCatalogOut, status_code=201)
def create_product(
    data: ProductCatalogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    if db.query(ProductCatalog).filter(ProductCatalog.product_code == data.product_code).first():
        raise HTTPException(400, f"Product code '{data.product_code}' already exists")
    if data.barcode and db.query(ProductCatalog).filter(ProductCatalog.barcode == data.barcode).first():
        raise HTTPException(400, f"Barcode '{data.barcode}' already in use")
    product = ProductCatalog(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=ProductCatalogOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductCatalogOut)
def update_product(
    product_id: int,
    data: ProductCatalogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    updates = data.model_dump(exclude_none=True)
    # validate barcode uniqueness if changing it
    if "barcode" in updates and updates["barcode"]:
        conflict = (
            db.query(ProductCatalog)
            .filter(
                ProductCatalog.barcode == updates["barcode"],
                ProductCatalog.id != product_id,
            )
            .first()
        )
        if conflict:
            raise HTTPException(400, f"Barcode '{updates['barcode']}' already in use")
    for field, value in updates.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    product.is_active = False
    db.commit()
    return {"message": f"Product '{product.name}' deactivated"}


@router.post("/products/{product_id}/barcode", response_model=BarcodeOut)
def generate_product_barcode(
    product_id: int,
    req: BarcodeGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a barcode for a product and assign it to the catalog entry."""
    if current_user.role.name not in ADMIN_ROLES + ("scanner", "packer"):
        raise HTTPException(403, "Insufficient permissions")
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    barcode_str = generate_barcode(product_id, prefix=req.prefix)
    # Assign to product catalog
    product.barcode = barcode_str

    entity_id = req.entity_id if req.entity_id is not None else product_id
    entry = register_barcode(
        db=db,
        barcode=barcode_str,
        entity_type=req.entity_type,
        entity_id=entity_id,
        product_id=product_id,
        user_id=current_user.id,
    )
    db.commit()
    db.refresh(entry)
    return entry


# ═══════════════════════════════════════════════════════════════
# PRICE RULES
# ═══════════════════════════════════════════════════════════════

@router.get("/price-rules", response_model=List[PriceRuleOut])
def list_price_rules(
    product_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PriceRule)
    if product_id:
        q = q.filter(PriceRule.product_id == product_id)
    if is_active is not None:
        q = q.filter(PriceRule.is_active == is_active)
    return q.order_by(PriceRule.id.desc()).all()


@router.post("/price-rules", response_model=PriceRuleOut, status_code=201)
def create_price_rule(
    data: PriceRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    product = db.query(ProductCatalog).filter(ProductCatalog.id == data.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    rule = PriceRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/price-rules/{rule_id}")
def delete_price_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    rule = db.query(PriceRule).filter(PriceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(404, "Price rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Price rule deleted"}
