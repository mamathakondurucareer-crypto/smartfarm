"""Inventory management endpoints: items, transactions, suppliers, purchase orders."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.activity_log_service import log_activity
from backend.models.inventory import (
    InventoryCategory, InventoryItem, InventoryTransaction,
    PurchaseOrder, PurchaseOrderItem, Supplier,
)
from backend.schemas import (
    InventoryItemCreate, InventoryItemOut, InventoryTransactionCreate,
    SupplierCreate, PurchaseOrderCreate,
)
from backend.utils.helpers import generate_code

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


# ── Categories ──
@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return db.query(InventoryCategory).all()


# ── Items ──
@router.get("/items", response_model=list[InventoryItemOut])
def list_items(
    category_id: Optional[int] = None,
    low_stock: bool = False,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(InventoryItem).filter(InventoryItem.is_active == True)
    if category_id:
        q = q.filter(InventoryItem.category_id == category_id)
    if low_stock:
        q = q.filter(InventoryItem.current_stock <= InventoryItem.reorder_point)
    if location:
        q = q.filter(InventoryItem.location == location)
    return q.order_by(InventoryItem.name).all()


@router.post("/items", response_model=InventoryItemOut, status_code=201)
def create_item(data: InventoryItemCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    item = InventoryItem(**data.model_dump(), total_value=data.current_stock * data.unit_cost)
    db.add(item)
    log_activity(db, "CREATE_ITEM", "inventory", username=current_user.username,
                 user_id=current_user.id, entity_type="InventoryItem",
                 description=f"Inventory item created: {data.name} ({data.unit})")
    db.commit()
    db.refresh(item)
    return item


@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    recent_txns = db.query(InventoryTransaction).filter(
        InventoryTransaction.item_id == item_id
    ).order_by(InventoryTransaction.transaction_date.desc()).limit(20).all()
    return {"item": InventoryItemOut.model_validate(item), "recent_transactions": recent_txns, "stock_status": item.stock_status}


# ── Transactions ──
@router.post("/transactions", status_code=201)
def create_transaction(data: InventoryTransactionCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    item = db.query(InventoryItem).filter(InventoryItem.id == data.item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    # Update stock
    if data.transaction_type in ("purchase", "production_in", "return", "adjustment"):
        item.current_stock += data.quantity
    elif data.transaction_type in ("consumption", "wastage", "transfer"):
        if item.current_stock < data.quantity:
            raise HTTPException(400, f"Insufficient stock. Available: {item.current_stock}")
        item.current_stock -= data.quantity
    else:
        raise HTTPException(400, f"Unknown transaction type: {data.transaction_type}")

    item.total_value = item.current_stock * item.unit_cost
    total_cost = data.quantity * data.unit_cost

    txn = InventoryTransaction(
        **data.model_dump(),
        total_cost=total_cost,
        balance_after=item.current_stock,
    )
    db.add(txn)
    log_activity(db, "INVENTORY_TRANSACTION", "inventory", username=current_user.username,
                 user_id=current_user.id, entity_type="InventoryItem", entity_id=data.item_id,
                 description=f"{data.transaction_type.upper()} {data.quantity} {item.unit} of {item.name}")
    db.commit()
    db.refresh(txn)

    result = {"id": txn.id, "balance_after": txn.balance_after, "stock_status": item.stock_status}
    if item.is_low_stock:
        result["warning"] = f"LOW STOCK: {item.name} at {item.current_stock} {item.unit} (reorder point: {item.reorder_point})"
    return result


@router.get("/transactions")
def list_transactions(
    item_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(InventoryTransaction)
    if item_id:
        q = q.filter(InventoryTransaction.item_id == item_id)
    if transaction_type:
        q = q.filter(InventoryTransaction.transaction_type == transaction_type)
    if start_date:
        q = q.filter(InventoryTransaction.transaction_date >= start_date)
    if end_date:
        q = q.filter(InventoryTransaction.transaction_date <= end_date)
    return q.order_by(InventoryTransaction.created_at.desc()).limit(200).all()


# ── Low Stock Report ──
@router.get("/low-stock")
def low_stock_report(db: Session = Depends(get_db)):
    items = db.query(InventoryItem).filter(
        InventoryItem.is_active == True,
        InventoryItem.current_stock <= InventoryItem.reorder_point,
    ).all()
    return [{
        "item_code": i.item_code, "name": i.name, "current_stock": i.current_stock,
        "reorder_point": i.reorder_point, "reorder_qty": i.reorder_quantity,
        "unit": i.unit, "location": i.location,
    } for i in items]


# ── Suppliers ──
@router.get("/suppliers")
def list_suppliers(supplier_type: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Supplier).filter(Supplier.is_active == True)
    if supplier_type:
        q = q.filter(Supplier.supplier_type == supplier_type)
    return q.order_by(Supplier.name).all()


@router.post("/suppliers", status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


# ── Purchase Orders ──
@router.post("/purchase-orders", status_code=201)
def create_po(data: PurchaseOrderCreate, db: Session = Depends(get_db)):
    count = db.query(func.count(PurchaseOrder.id)).scalar()
    po = PurchaseOrder(
        po_number=generate_code("PO", count + 1),
        supplier_id=data.supplier_id,
        order_date=data.order_date,
        expected_delivery=data.expected_delivery,
        notes=data.notes,
    )
    db.add(po)
    db.flush()

    subtotal = 0
    gst_total = 0
    for item_data in data.items:
        total = item_data.quantity_ordered * item_data.unit_price
        gst = total * item_data.gst_rate / 100
        poi = PurchaseOrderItem(
            po_id=po.id, item_id=item_data.item_id,
            quantity_ordered=item_data.quantity_ordered,
            unit_price=item_data.unit_price,
            gst_rate=item_data.gst_rate,
            total_price=total + gst,
        )
        db.add(poi)
        subtotal += total
        gst_total += gst

    po.subtotal = subtotal
    po.gst_amount = gst_total
    po.total_amount = subtotal + gst_total
    db.commit()
    db.refresh(po)
    return {"po_number": po.po_number, "total_amount": po.total_amount}


@router.get("/purchase-orders")
def list_pos(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(PurchaseOrder)
    if status:
        q = q.filter(PurchaseOrder.delivery_status == status)
    return q.order_by(PurchaseOrder.order_date.desc()).limit(50).all()


# ── Valuation Report ──
@router.get("/valuation")
def inventory_valuation(db: Session = Depends(get_db)):
    items = db.query(InventoryItem).filter(InventoryItem.is_active == True).all()
    total_value = sum(i.current_stock * i.unit_cost for i in items)
    by_category = {}
    for i in items:
        cat = i.category_id
        if cat not in by_category:
            by_category[cat] = 0
        by_category[cat] += i.current_stock * i.unit_cost
    return {
        "total_items": len(items),
        "total_value": round(total_value, 2),
        "by_category": by_category,
    }
