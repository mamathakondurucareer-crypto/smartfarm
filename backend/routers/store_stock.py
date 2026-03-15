"""Store stock management router."""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models.store import StoreConfig, ProductCatalog
from backend.models.supply_chain import StoreStock, FarmSupplyTransfer
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import StoreStockOut, StoreStockAdjust

router = APIRouter(prefix="/api/store/stock", tags=["Store — Stock"])

ADMIN_ROLES = ("admin", "store_manager")


def _get_or_create_stock(db: Session, product: ProductCatalog) -> StoreStock:
    stock = db.query(StoreStock).filter(StoreStock.product_id == product.id).first()
    if not stock:
        stock = StoreStock(
            product_id=product.id,
            unit=product.unit,
            current_qty=0,
            reserved_qty=0,
            avg_cost_per_unit=product.cost_price,
            location="floor",
            updated_at=datetime.now(timezone.utc),
        )
        db.add(stock)
        db.flush()
    return stock


@router.get("", response_model=List[dict])
def list_all_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """All stock levels with embedded product information."""
    stocks = (
        db.query(StoreStock)
        .options(joinedload(StoreStock.product))
        .all()
    )
    result = []
    for s in stocks:
        result.append({
            "id": s.id,
            "product_id": s.product_id,
            "product_code": s.product.product_code if s.product else None,
            "product_name": s.product.name if s.product else None,
            "category": s.product.category if s.product else None,
            "current_qty": s.current_qty,
            "reserved_qty": s.reserved_qty,
            "available_qty": s.available_qty,
            "unit": s.unit,
            "avg_cost_per_unit": s.avg_cost_per_unit,
            "total_value": s.total_value,
            "last_received_at": s.last_received_at,
            "expiry_date": s.expiry_date,
            "location": s.location,
            "updated_at": s.updated_at,
        })
    return result


@router.get("/low", response_model=List[dict])
def low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Products whose current_qty is below the store low_stock_threshold."""
    cfg = db.query(StoreConfig).first()
    threshold = cfg.low_stock_threshold if cfg else 10

    stocks = (
        db.query(StoreStock)
        .options(joinedload(StoreStock.product))
        .filter(StoreStock.current_qty <= threshold)
        .all()
    )
    result = []
    for s in stocks:
        result.append({
            "product_id": s.product_id,
            "product_name": s.product.name if s.product else None,
            "current_qty": s.current_qty,
            "available_qty": s.available_qty,
            "unit": s.unit,
            "threshold": threshold,
            "location": s.location,
        })
    return result


@router.get("/{product_id}", response_model=dict)
def get_product_stock(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    stock = db.query(StoreStock).filter(StoreStock.product_id == product_id).first()
    if not stock:
        raise HTTPException(404, "No stock record found for this product")

    return {
        "id": stock.id,
        "product_id": stock.product_id,
        "product_code": product.product_code,
        "product_name": product.name,
        "category": product.category,
        "current_qty": stock.current_qty,
        "reserved_qty": stock.reserved_qty,
        "available_qty": stock.available_qty,
        "unit": stock.unit,
        "avg_cost_per_unit": stock.avg_cost_per_unit,
        "total_value": stock.total_value,
        "last_received_at": stock.last_received_at,
        "expiry_date": stock.expiry_date,
        "location": stock.location,
        "updated_at": stock.updated_at,
    }


@router.post("/adjust")
def adjust_stock(
    data: StoreStockAdjust,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manual stock adjustment (positive = add, negative = remove)."""
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    product = db.query(ProductCatalog).filter(ProductCatalog.id == data.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    stock = _get_or_create_stock(db, product)
    new_qty = stock.current_qty + data.adjustment_qty
    if new_qty < 0:
        raise HTTPException(400, f"Cannot reduce stock below zero. Current: {stock.current_qty}")
    stock.current_qty = round(new_qty, 4)
    if data.location:
        stock.location = data.location
    stock.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "message": "Stock adjusted",
        "product_id": data.product_id,
        "adjustment_qty": data.adjustment_qty,
        "new_qty": stock.current_qty,
        "reason": data.reason,
    }


@router.post("/receive")
def receive_stock_from_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Receive stock into store from a farm supply transfer (alias endpoint)."""
    transfer = db.query(FarmSupplyTransfer).filter(FarmSupplyTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    if transfer.status != "in_transit":
        raise HTTPException(400, f"Transfer is '{transfer.status}', expected 'in_transit'")

    product = db.query(ProductCatalog).filter(ProductCatalog.id == transfer.product_id).first()
    if not product:
        raise HTTPException(404, "Product in transfer not found")

    stock = _get_or_create_stock(db, product)
    qty = transfer.quantity_transferred

    # Weighted-average cost update
    total_existing_value = stock.current_qty * stock.avg_cost_per_unit
    total_new_value = qty * transfer.cost_per_unit
    new_total_qty = stock.current_qty + qty
    if new_total_qty > 0:
        stock.avg_cost_per_unit = round(
            (total_existing_value + total_new_value) / new_total_qty, 4
        )
    stock.current_qty = round(new_total_qty, 4)
    stock.last_received_at = datetime.now(timezone.utc)
    stock.updated_at = datetime.now(timezone.utc)

    transfer.status = "received"
    transfer.received_by = current_user.id
    transfer.received_at = datetime.now(timezone.utc)

    db.commit()
    return {
        "message": "Stock received",
        "transfer_id": transfer_id,
        "qty_received": qty,
        "new_stock_qty": stock.current_qty,
    }
