"""Farm-to-store supply chain (transfers) router."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models.store import ProductCatalog
from backend.models.supply_chain import FarmSupplyTransfer, StoreStock
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import FarmSupplyTransferCreate, FarmSupplyTransferOut, TransferReceive, TransferReject

router = APIRouter(prefix="/api/supply-chain", tags=["Supply Chain"])

SENDER_ROLES = ("admin", "manager", "supervisor", "store_manager")


def _make_transfer_code(db: Session) -> str:
    count = db.query(FarmSupplyTransfer).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TRF-{ts}-{count + 1:04d}"


@router.get("/transfers", response_model=List[FarmSupplyTransferOut])
def list_transfers(
    status: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(FarmSupplyTransfer)
    if status:
        q = q.filter(FarmSupplyTransfer.status == status)
    if source_type:
        q = q.filter(FarmSupplyTransfer.source_type == source_type)
    if product_id:
        q = q.filter(FarmSupplyTransfer.product_id == product_id)
    if start_date:
        q = q.filter(FarmSupplyTransfer.transfer_date >= start_date)
    if end_date:
        q = q.filter(FarmSupplyTransfer.transfer_date <= end_date)
    return q.order_by(FarmSupplyTransfer.transfer_date.desc()).limit(limit).all()


@router.post("/transfers", response_model=FarmSupplyTransferOut, status_code=201)
def create_transfer(
    data: FarmSupplyTransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in SENDER_ROLES:
        raise HTTPException(403, "Manager or supervisor role required")
    product = db.query(ProductCatalog).filter(ProductCatalog.id == data.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found in catalog")

    total_cost = round(data.quantity_transferred * data.cost_per_unit, 2)
    transfer = FarmSupplyTransfer(
        transfer_code=_make_transfer_code(db),
        transferred_by=current_user.id,
        total_cost=total_cost,
        status="in_transit",
        **data.model_dump(),
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


@router.get("/transfers/{transfer_id}", response_model=FarmSupplyTransferOut)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transfer = db.query(FarmSupplyTransfer).filter(FarmSupplyTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    return transfer


@router.put("/transfers/{transfer_id}/receive", response_model=FarmSupplyTransferOut)
def receive_transfer(
    transfer_id: int,
    data: TransferReceive,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a transfer as received and update store stock using weighted-average cost."""
    transfer = db.query(FarmSupplyTransfer).filter(FarmSupplyTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    if transfer.status not in ("pending", "in_transit"):
        raise HTTPException(400, f"Transfer already '{transfer.status}'")

    product = db.query(ProductCatalog).filter(ProductCatalog.id == transfer.product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    qty = data.received_qty if data.received_qty is not None else transfer.quantity_transferred

    # Update or create store stock
    stock = db.query(StoreStock).filter(StoreStock.product_id == transfer.product_id).first()
    if not stock:
        stock = StoreStock(
            product_id=transfer.product_id,
            unit=transfer.unit,
            current_qty=0,
            reserved_qty=0,
            avg_cost_per_unit=transfer.cost_per_unit,
            location="floor",
        )
        db.add(stock)
        db.flush()

    # Weighted-average cost
    existing_value = stock.current_qty * stock.avg_cost_per_unit
    new_value = qty * transfer.cost_per_unit
    new_qty = stock.current_qty + qty
    if new_qty > 0:
        stock.avg_cost_per_unit = round((existing_value + new_value) / new_qty, 4)
    stock.current_qty = round(new_qty, 4)
    stock.last_received_at = datetime.now(timezone.utc)
    stock.updated_at = datetime.now(timezone.utc)

    transfer.status = "received"
    transfer.received_by = current_user.id
    transfer.received_at = datetime.now(timezone.utc)
    if data.notes:
        transfer.notes = data.notes

    db.commit()
    db.refresh(transfer)
    return transfer


@router.put("/transfers/{transfer_id}/reject", response_model=FarmSupplyTransferOut)
def reject_transfer(
    transfer_id: int,
    data: TransferReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in SENDER_ROLES + ("cashier",):
        raise HTTPException(403, "Insufficient permissions to reject transfer")
    transfer = db.query(FarmSupplyTransfer).filter(FarmSupplyTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    if transfer.status not in ("pending", "in_transit"):
        raise HTTPException(400, f"Transfer already '{transfer.status}'")

    transfer.status = "rejected"
    transfer.rejection_reason = data.rejection_reason
    transfer.received_by = current_user.id
    transfer.received_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(transfer)
    return transfer
