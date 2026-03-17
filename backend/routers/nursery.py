"""Nursery management router."""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.nursery import NurseryBatch, NurseryOrder

router = APIRouter(prefix="/api/nursery", tags=["Nursery Management"])
MGMT_ROLES = ("admin", "manager", "supervisor")

# ── Schemas ──────────────────────────────────────────────────────────────
class NurseryBatchCreate(BaseModel):
    batch_code: str
    species: str
    category: str = "vegetable"
    sowing_date: date
    expected_ready_date: Optional[date] = None
    tray_count: int = 0
    cells_per_tray: int = 98
    germination_pct: float = 0.0
    seedlings_ready: int = 0
    status: str = "sown"
    notes: Optional[str] = None

class NurseryBatchUpdate(BaseModel):
    species: Optional[str] = None
    category: Optional[str] = None
    expected_ready_date: Optional[date] = None
    tray_count: Optional[int] = None
    cells_per_tray: Optional[int] = None
    germination_pct: Optional[float] = None
    seedlings_ready: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class NurseryBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_code: str
    species: str
    category: str
    sowing_date: date
    expected_ready_date: Optional[date]
    tray_count: int
    cells_per_tray: int
    germination_pct: float
    seedlings_ready: int
    status: str
    notes: Optional[str]
    is_active: bool

class NurseryOrderCreate(BaseModel):
    batch_id: Optional[int] = None
    buyer_name: str
    buyer_contact: Optional[str] = None
    species: str
    quantity: int = 0
    price_per_seedling: float = 0.0
    order_date: date
    dispatch_date: Optional[date] = None
    status: str = "pending"
    notes: Optional[str] = None

class NurseryOrderUpdate(BaseModel):
    buyer_name: Optional[str] = None
    buyer_contact: Optional[str] = None
    quantity: Optional[int] = None
    price_per_seedling: Optional[float] = None
    dispatch_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class NurseryOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_id: Optional[int]
    buyer_name: str
    buyer_contact: Optional[str]
    species: str
    quantity: int
    price_per_seedling: float
    total_amount: float
    order_date: date
    dispatch_date: Optional[date]
    status: str
    notes: Optional[str]

# ── Batches ──────────────────────────────────────────────────────────────
@router.get("/batches", response_model=List[NurseryBatchOut])
def list_batches(status: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(NurseryBatch).filter(NurseryBatch.is_active == True)
    if status:
        q = q.filter(NurseryBatch.status == status)
    return q.order_by(NurseryBatch.sowing_date.desc()).all()

@router.post("/batches", response_model=NurseryBatchOut, status_code=201)
def create_batch(data: NurseryBatchCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if db.query(NurseryBatch).filter(NurseryBatch.batch_code == data.batch_code).first():
        raise HTTPException(400, "Batch code already exists")
    obj = NurseryBatch(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return NurseryBatchOut.model_validate(obj)

@router.put("/batches/{batch_id}", response_model=NurseryBatchOut)
def update_batch(batch_id: int, data: NurseryBatchUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(NurseryBatch).filter(NurseryBatch.id == batch_id, NurseryBatch.is_active == True).first()
    if not obj:
        raise HTTPException(404, "Batch not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return NurseryBatchOut.model_validate(obj)

@router.delete("/batches/{batch_id}", status_code=204)
def delete_batch(batch_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(NurseryBatch).filter(NurseryBatch.id == batch_id, NurseryBatch.is_active == True).first()
    if not obj:
        raise HTTPException(404, "Batch not found")
    obj.is_active = False
    db.commit()

@router.get("/batches/summary")
def batches_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    batches = db.query(NurseryBatch).filter(NurseryBatch.is_active == True).all()
    total_capacity = sum(b.tray_count * b.cells_per_tray for b in batches)
    total_ready = sum(b.seedlings_ready for b in batches)
    return {
        "total_batches": len(batches),
        "total_capacity": total_capacity,
        "total_ready": total_ready,
        "by_status": {s: sum(1 for b in batches if b.status == s) for s in ["sown", "germinated", "hardening", "ready", "dispatched"]},
    }

# ── Orders ────────────────────────────────────────────────────────────────
@router.get("/orders", response_model=List[NurseryOrderOut])
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(NurseryOrder)
    if status:
        q = q.filter(NurseryOrder.status == status)
    return q.order_by(NurseryOrder.order_date.desc()).all()

@router.post("/orders", response_model=NurseryOrderOut, status_code=201)
def create_order(data: NurseryOrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total = data.quantity * data.price_per_seedling
    obj = NurseryOrder(**{**data.model_dump(), "total_amount": total})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return NurseryOrderOut.model_validate(obj)

@router.put("/orders/{order_id}", response_model=NurseryOrderOut)
def update_order(order_id: int, data: NurseryOrderUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(NurseryOrder).filter(NurseryOrder.id == order_id).first()
    if not obj:
        raise HTTPException(404, "Order not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    if data.quantity or data.price_per_seedling:
        obj.total_amount = obj.quantity * obj.price_per_seedling
    db.commit()
    db.refresh(obj)
    return NurseryOrderOut.model_validate(obj)

@router.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(NurseryOrder).filter(NurseryOrder.id == order_id).first()
    if not obj:
        raise HTTPException(404, "Order not found")
    db.delete(obj)
    db.commit()
