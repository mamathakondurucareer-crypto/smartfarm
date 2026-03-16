"""Packing orders and barcode registry router."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models.packing import PackingOrder, PackingOrderItem, BarcodeRegistry
from backend.models.store import ProductCatalog
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.barcode_service import generate_barcode, register_barcode, resolve_barcode
from backend.schemas import (
    PackingOrderCreate, PackingOrderOut, PackItemRequest,
    BarcodeOut, BarcodeGenerateRequest, BarcodeScanResult,
)

router = APIRouter(prefix="/api/packing", tags=["Packing & Barcodes"])

PACKING_ROLES = ("admin", "manager", "store_manager", "packer", "supervisor")
ADMIN_ROLES = ("admin", "store_manager", "manager")


def _packing_code(db: Session) -> str:
    count = db.query(PackingOrder).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"PKG-{ts}-{count + 1:04d}"


# ═══════════════════════════════════════════════════════════════
# PACKING ORDERS
# ═══════════════════════════════════════════════════════════════

@router.get("/orders", response_model=List[PackingOrderOut])
def list_packing_orders(
    status: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PackingOrder).options(joinedload(PackingOrder.items))
    if status:
        q = q.filter(PackingOrder.status == status)
    if assigned_to:
        q = q.filter(PackingOrder.assigned_to == assigned_to)
    if start_date:
        q = q.filter(PackingOrder.scheduled_date >= start_date)
    if end_date:
        q = q.filter(PackingOrder.scheduled_date <= end_date)
    return q.order_by(PackingOrder.created_at.desc()).limit(limit).all()


@router.post("/orders", response_model=PackingOrderOut, status_code=201)
def create_packing_order(
    data: PackingOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in PACKING_ROLES:
        raise HTTPException(403, "Packing role required")
    if not data.items:
        raise HTTPException(400, "Packing order must have at least one item")

    order = PackingOrder(
        packing_order_code=_packing_code(db),
        order_ref_type=data.order_ref_type,
        order_ref_id=data.order_ref_id,
        assigned_to=data.assigned_to,
        scheduled_date=data.scheduled_date,
        notes=data.notes,
        total_items=len(data.items),
        status="pending",
    )
    db.add(order)
    db.flush()

    for item_data in data.items:
        product = db.query(ProductCatalog).filter(ProductCatalog.id == item_data.product_id).first()
        if not product:
            raise HTTPException(404, f"Product id={item_data.product_id} not found")
        item = PackingOrderItem(
            packing_order_id=order.id,
            product_id=item_data.product_id,
            product_name=item_data.product_name or product.name,
            quantity_required=item_data.quantity_required,
            quantity_packed=0,
            packaging_type=item_data.packaging_type,
            expiry_date=item_data.expiry_date,
            notes=item_data.notes,
        )
        db.add(item)

    db.commit()
    order = (
        db.query(PackingOrder)
        .options(joinedload(PackingOrder.items))
        .filter(PackingOrder.id == order.id)
        .first()
    )
    return order


@router.get("/orders/{order_id}", response_model=PackingOrderOut)
def get_packing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(PackingOrder)
        .options(joinedload(PackingOrder.items))
        .filter(PackingOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(404, "Packing order not found")
    return order


@router.put("/orders/{order_id}", response_model=PackingOrderOut)
def update_packing_order(
    order_id: int,
    notes: Optional[str] = None,
    assigned_to: Optional[int] = None,
    scheduled_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or manager role required")
    order = db.query(PackingOrder).filter(PackingOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Packing order not found")
    if notes is not None:
        order.notes = notes
    if assigned_to is not None:
        order.assigned_to = assigned_to
    if scheduled_date is not None:
        order.scheduled_date = scheduled_date
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/start")
def start_packing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in PACKING_ROLES:
        raise HTTPException(403, "Packing role required")
    order = db.query(PackingOrder).filter(PackingOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Packing order not found")
    if order.status != "pending":
        raise HTTPException(400, f"Order is '{order.status}', not pending")
    order.status = "in_progress"
    order.started_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Packing order started", "order_id": order_id}


@router.post("/orders/{order_id}/items/{item_id}/pack")
def pack_item(
    order_id: int,
    item_id: int,
    data: PackItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in PACKING_ROLES:
        raise HTTPException(403, "Packing role required")
    order = db.query(PackingOrder).filter(PackingOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "Packing order not found")
    item = db.query(PackingOrderItem).filter(
        PackingOrderItem.id == item_id,
        PackingOrderItem.packing_order_id == order_id,
    ).first()
    if not item:
        raise HTTPException(404, "Packing order item not found")
    if data.quantity_packed > item.quantity_required:
        raise HTTPException(400, "Packed quantity exceeds required quantity")

    item.quantity_packed = data.quantity_packed
    item.label_printed = data.label_printed
    item.barcode_generated = data.barcode_generated
    db.commit()
    return {
        "message": "Item updated",
        "item_id": item_id,
        "quantity_packed": item.quantity_packed,
    }


@router.post("/orders/{order_id}/complete")
def complete_packing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in PACKING_ROLES:
        raise HTTPException(403, "Packing role required")
    order = (
        db.query(PackingOrder)
        .options(joinedload(PackingOrder.items))
        .filter(PackingOrder.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(404, "Packing order not found")
    if order.status not in ("in_progress", "paused"):
        raise HTTPException(400, f"Order is '{order.status}', cannot complete")

    order.status = "completed"
    order.completed_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Packing order completed", "order_id": order_id}


# ═══════════════════════════════════════════════════════════════
# BARCODES
# ═══════════════════════════════════════════════════════════════

@router.get("/barcodes", response_model=List[BarcodeOut])
def list_barcodes(
    entity_type: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(BarcodeRegistry)
    if entity_type:
        q = q.filter(BarcodeRegistry.entity_type == entity_type)
    if product_id:
        q = q.filter(BarcodeRegistry.product_id == product_id)
    if is_active is not None:
        q = q.filter(BarcodeRegistry.is_active == is_active)
    return q.order_by(BarcodeRegistry.generated_at.desc()).limit(limit).all()


@router.post("/barcodes/generate", response_model=BarcodeOut, status_code=201)
def generate_barcode_for_entity(
    data: BarcodeGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(ProductCatalog).filter(ProductCatalog.id == data.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    barcode_str = generate_barcode(data.product_id, prefix=data.prefix)
    entity_id = data.entity_id if data.entity_id is not None else data.product_id

    entry = register_barcode(
        db=db,
        barcode=barcode_str,
        entity_type=data.entity_type,
        entity_id=entity_id,
        product_id=data.product_id,
        user_id=current_user.id,
    )
    # Update product catalog barcode if entity_type is product
    if data.entity_type == "product":
        product.barcode = barcode_str

    db.commit()
    db.refresh(entry)
    return entry


@router.get("/barcodes/scan/{barcode}", response_model=BarcodeScanResult)
def scan_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = resolve_barcode(db, barcode)
    if result:
        db.commit()
        return BarcodeScanResult(barcode=barcode, found=True, result=result)
    return BarcodeScanResult(barcode=barcode, found=False, message="Barcode not found in system")
