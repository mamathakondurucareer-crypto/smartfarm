"""Feed Production router — BSF, Azolla, Duckweed, Feed Mill, Feed Inventory."""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.feed_production import BSFColony, AzollaLog, DuckweedLog, FeedMillBatch, FeedInventory

router = APIRouter(prefix="/api/feed-production", tags=["Feed Production"])

MGMT_ROLES = ("admin", "manager", "supervisor")

# ──────────────────────────────────────────────────────── Schemas ──────
class BSFColonyCreate(BaseModel):
    batch_code: str
    colony_stage: str = "egg"
    substrate_type: str = "kitchen_waste"
    daily_yield_kg: float = 0.0
    moisture_pct: float = 60.0
    larvae_age_days: int = 0
    colony_health: str = "good"
    notes: Optional[str] = None

class BSFColonyUpdate(BaseModel):
    colony_stage: Optional[str] = None
    substrate_type: Optional[str] = None
    daily_yield_kg: Optional[float] = None
    moisture_pct: Optional[float] = None
    larvae_age_days: Optional[int] = None
    colony_health: Optional[str] = None
    notes: Optional[str] = None

class BSFColonyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_code: str
    colony_stage: str
    substrate_type: str
    daily_yield_kg: float
    moisture_pct: float
    larvae_age_days: int
    colony_health: str
    notes: Optional[str]
    is_active: bool

class AzollaLogCreate(BaseModel):
    bed_id: str
    log_date: date
    harvest_kg: float = 0.0
    moisture_pct: float = 90.0
    protein_pct: float = 25.0
    area_sqm: float = 0.0
    notes: Optional[str] = None

class AzollaLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bed_id: str
    log_date: date
    harvest_kg: float
    moisture_pct: float
    protein_pct: float
    area_sqm: float
    notes: Optional[str]

class DuckweedLogCreate(BaseModel):
    pond_id: str
    log_date: date
    yield_kg: float = 0.0
    water_tds: float = 0.0
    ph: float = 7.0
    allocated_to: str = "fish"
    notes: Optional[str] = None

class DuckweedLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pond_id: str
    log_date: date
    yield_kg: float
    water_tds: float
    ph: float
    allocated_to: str
    notes: Optional[str]

class FeedMillBatchCreate(BaseModel):
    batch_code: str
    formulation: str
    date_produced: date
    quantity_kg: float = 0.0
    moisture_pct: float = 12.0
    protein_pct: float = 28.0
    aflatoxin_ppb: float = 0.0
    pellet_durability_pct: float = 98.0
    target_species: str = "fish"
    passed_qa: bool = True
    notes: Optional[str] = None

class FeedMillBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_code: str
    formulation: str
    date_produced: date
    quantity_kg: float
    moisture_pct: float
    protein_pct: float
    aflatoxin_ppb: float
    pellet_durability_pct: float
    target_species: str
    passed_qa: bool
    notes: Optional[str]
    is_active: bool

class FeedInventoryCreate(BaseModel):
    feed_type: str
    quantity_kg: float = 0.0
    unit_cost_per_kg: float = 0.0
    source: str = "on-farm"
    received_date: date
    expiry_date: Optional[date] = None
    batch_code: Optional[str] = None
    notes: Optional[str] = None

class FeedInventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    feed_type: str
    quantity_kg: float
    unit_cost_per_kg: float
    source: str
    received_date: date
    expiry_date: Optional[date]
    batch_code: Optional[str]
    notes: Optional[str]

# ──────────────────────────────────────────────────────── BSF ──────────
@router.get("/bsf", response_model=List[BSFColonyOut])
def list_bsf(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(BSFColony).filter(BSFColony.is_active == True).all()

@router.post("/bsf", response_model=BSFColonyOut, status_code=201)
def create_bsf(data: BSFColonyCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    if db.query(BSFColony).filter(BSFColony.batch_code == data.batch_code).first():
        raise HTTPException(400, "Batch code already exists")
    obj = BSFColony(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return BSFColonyOut.model_validate(obj)

@router.put("/bsf/{colony_id}", response_model=BSFColonyOut)
def update_bsf(colony_id: int, data: BSFColonyUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = db.query(BSFColony).filter(BSFColony.id == colony_id, BSFColony.is_active == True).first()
    if not obj:
        raise HTTPException(404, "BSF colony not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return BSFColonyOut.model_validate(obj)

@router.delete("/bsf/{colony_id}", status_code=204)
def delete_bsf(colony_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in ("admin", "manager"):
        raise HTTPException(403, "Admin/manager role required")
    obj = db.query(BSFColony).filter(BSFColony.id == colony_id).first()
    if not obj:
        raise HTTPException(404, "BSF colony not found")
    obj.is_active = False
    db.commit()

# ──────────────────────────────────────────────────────── Azolla ───────
@router.get("/azolla", response_model=List[AzollaLogOut])
def list_azolla(bed_id: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(AzollaLog)
    if bed_id:
        q = q.filter(AzollaLog.bed_id == bed_id)
    return q.order_by(AzollaLog.log_date.desc()).all()

@router.post("/azolla", response_model=AzollaLogOut, status_code=201)
def create_azolla(data: AzollaLogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = AzollaLog(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return AzollaLogOut.model_validate(obj)

# ──────────────────────────────────────────────────────── Duckweed ─────
@router.get("/duckweed", response_model=List[DuckweedLogOut])
def list_duckweed(pond_id: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(DuckweedLog)
    if pond_id:
        q = q.filter(DuckweedLog.pond_id == pond_id)
    return q.order_by(DuckweedLog.log_date.desc()).all()

@router.post("/duckweed", response_model=DuckweedLogOut, status_code=201)
def create_duckweed(data: DuckweedLogCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = DuckweedLog(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return DuckweedLogOut.model_validate(obj)

# ──────────────────────────────────────────────────────── Feed Mill ────
@router.get("/batches", response_model=List[FeedMillBatchOut])
def list_batches(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(FeedMillBatch).filter(FeedMillBatch.is_active == True).order_by(FeedMillBatch.date_produced.desc()).all()

@router.post("/batches", response_model=FeedMillBatchOut, status_code=201)
def create_batch(data: FeedMillBatchCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    if db.query(FeedMillBatch).filter(FeedMillBatch.batch_code == data.batch_code).first():
        raise HTTPException(400, "Batch code already exists")
    obj = FeedMillBatch(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return FeedMillBatchOut.model_validate(obj)

@router.delete("/batches/{batch_id}", status_code=204)
def delete_batch(batch_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in ("admin", "manager"):
        raise HTTPException(403, "Admin/manager role required")
    obj = db.query(FeedMillBatch).filter(FeedMillBatch.id == batch_id).first()
    if not obj:
        raise HTTPException(404, "Feed mill batch not found")
    obj.is_active = False
    db.commit()

# ──────────────────────────────────────────────────────── Inventory ────
@router.get("/inventory", response_model=List[FeedInventoryOut])
def list_inventory(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(FeedInventory).order_by(FeedInventory.received_date.desc()).all()

@router.post("/inventory", response_model=FeedInventoryOut, status_code=201)
def add_inventory(data: FeedInventoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = FeedInventory(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return FeedInventoryOut.model_validate(obj)

@router.delete("/inventory/{item_id}", status_code=204)
def delete_inventory(item_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(FeedInventory).filter(FeedInventory.id == item_id).first()
    if not obj:
        raise HTTPException(404, "Inventory item not found")
    db.delete(obj)
    db.commit()

# ──────────────────────────────────────────────────────── Self-sufficiency ──
@router.get("/self-sufficiency")
def self_sufficiency(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Return on-farm feed % vs purchased per feed type."""
    from sqlalchemy import func
    rows = db.query(
        FeedInventory.feed_type,
        func.sum(FeedInventory.quantity_kg).label("total_kg"),
        func.sum(FeedInventory.unit_cost_per_kg * FeedInventory.quantity_kg).label("total_cost")
    ).group_by(FeedInventory.feed_type).all()
    total_kg = sum(r.total_kg for r in rows) or 1
    result = []
    for r in rows:
        is_on_farm = "on_farm" in r.feed_type or r.feed_type in ("bsf", "azolla", "duckweed")
        result.append({
            "feed_type": r.feed_type,
            "total_kg": round(r.total_kg, 2),
            "total_cost": round(r.total_cost, 2),
            "pct_of_total": round(r.total_kg / total_kg * 100, 1),
            "source": "on-farm" if is_on_farm else "purchased",
        })
    on_farm_kg = sum(r["total_kg"] for r in result if r["source"] == "on-farm")
    return {
        "breakdown": result,
        "on_farm_pct": round(on_farm_kg / total_kg * 100, 1),
        "purchased_pct": round((total_kg - on_farm_kg) / total_kg * 100, 1),
    }
