"""QA & Traceability router."""
import uuid
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.qa_traceability import ProductLot, QualityTest, QAQuarantine

router = APIRouter(prefix="/api/qa", tags=["QA & Traceability"])
MGMT_ROLES = ("admin", "manager", "supervisor")

# ── Schemas ──────────────────────────────────────────────────────────────
class ProductLotCreate(BaseModel):
    lot_code: Optional[str] = None  # auto-generated if not provided
    product_type: str
    source_module: str = ""
    source_id: Optional[str] = None
    produced_date: date
    quantity: float = 0.0
    unit: str = "kg"
    harvest_team: Optional[str] = None
    notes: Optional[str] = None

class ProductLotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lot_code: str
    product_type: str
    source_module: str
    source_id: Optional[str]
    produced_date: date
    quantity: float
    unit: str
    harvest_team: Optional[str]
    qr_code: Optional[str]
    status: str
    notes: Optional[str]

class QualityTestCreate(BaseModel):
    lot_id: int
    test_type: str
    test_date: date
    result_value: Optional[float] = None
    result_text: Optional[str] = None
    passed: bool = True
    tester: str
    lab: Optional[str] = None
    notes: Optional[str] = None

class QualityTestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lot_id: int
    test_type: str
    test_date: date
    result_value: Optional[float]
    result_text: Optional[str]
    passed: bool
    tester: str
    lab: Optional[str]
    notes: Optional[str]

class QuarantineCreate(BaseModel):
    lot_id: int
    reason: str
    quarantine_date: date
    notes: Optional[str] = None

class QuarantineResolve(BaseModel):
    resolved_by: str
    resolution: str

class QuarantineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lot_id: int
    reason: str
    quarantine_date: date
    resolved_date: Optional[date]
    resolved_by: Optional[str]
    resolution: Optional[str]
    is_resolved: bool

# ── Product Lots ─────────────────────────────────────────────────────────
@router.get("/lots", response_model=List[ProductLotOut])
def list_lots(product_type: Optional[str] = None, status: Optional[str] = None,
              db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(ProductLot)
    if product_type:
        q = q.filter(ProductLot.product_type == product_type)
    if status:
        q = q.filter(ProductLot.status == status)
    return q.order_by(ProductLot.produced_date.desc()).all()

@router.post("/lots", response_model=ProductLotOut, status_code=201)
def create_lot(data: ProductLotCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    lot_code = data.lot_code or f"LOT-{data.product_type.upper()[:3]}-{data.produced_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    qr_code = f"SF-QR-{lot_code}"
    obj = ProductLot(**{**data.model_dump(exclude={"lot_code"}), "lot_code": lot_code, "qr_code": qr_code})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ProductLotOut.model_validate(obj)

@router.get("/lots/{lot_id}", response_model=ProductLotOut)
def get_lot(lot_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(ProductLot).filter(ProductLot.id == lot_id).first()
    if not obj:
        raise HTTPException(404, "Lot not found")
    return ProductLotOut.model_validate(obj)

@router.get("/lots/trace/{lot_code}")
def trace_lot(lot_code: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Full provenance trace for a lot."""
    obj = db.query(ProductLot).filter(ProductLot.lot_code == lot_code).first()
    if not obj:
        raise HTTPException(404, "Lot not found")
    tests = db.query(QualityTest).filter(QualityTest.lot_id == obj.id).all()
    qrs = db.query(QAQuarantine).filter(QAQuarantine.lot_id == obj.id).all()
    return {
        "lot": ProductLotOut.model_validate(obj),
        "quality_tests": [QualityTestOut.model_validate(t) for t in tests],
        "quarantine": [QuarantineOut.model_validate(q) for q in qrs],
        "all_passed": all(t.passed for t in tests),
    }

@router.patch("/lots/{lot_id}/status")
def update_lot_status(lot_id: int, status: str = Query(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = db.query(ProductLot).filter(ProductLot.id == lot_id).first()
    if not obj:
        raise HTTPException(404, "Lot not found")
    obj.status = status
    db.commit()
    return {"status": status}

# ── Quality Tests ────────────────────────────────────────────────────────
@router.get("/tests", response_model=List[QualityTestOut])
def list_tests(lot_id: Optional[int] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(QualityTest)
    if lot_id:
        q = q.filter(QualityTest.lot_id == lot_id)
    return q.order_by(QualityTest.test_date.desc()).all()

@router.post("/tests", response_model=QualityTestOut, status_code=201)
def create_test(data: QualityTestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    lot = db.query(ProductLot).filter(ProductLot.id == data.lot_id).first()
    if not lot:
        raise HTTPException(404, "Lot not found")
    obj = QualityTest(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return QualityTestOut.model_validate(obj)

# ── Quarantine ───────────────────────────────────────────────────────────
@router.get("/quarantine", response_model=List[QuarantineOut])
def list_quarantine(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(QAQuarantine).order_by(QAQuarantine.quarantine_date.desc()).all()

@router.post("/quarantine", response_model=QuarantineOut, status_code=201)
def create_quarantine(data: QuarantineCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    lot = db.query(ProductLot).filter(ProductLot.id == data.lot_id).first()
    if not lot:
        raise HTTPException(404, "Lot not found")
    lot.status = "quarantine"
    obj = QAQuarantine(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return QuarantineOut.model_validate(obj)

@router.put("/quarantine/{qr_id}/resolve", response_model=QuarantineOut)
def resolve_quarantine(qr_id: int, data: QuarantineResolve, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = db.query(QAQuarantine).filter(QAQuarantine.id == qr_id).first()
    if not obj:
        raise HTTPException(404, "Quarantine record not found")
    from datetime import date as date_cls
    obj.resolved_date = date_cls.today()
    obj.resolved_by = data.resolved_by
    obj.resolution = data.resolution
    obj.is_resolved = True
    lot = db.query(ProductLot).filter(ProductLot.id == obj.lot_id).first()
    if lot:
        lot.status = "released"
    db.commit()
    db.refresh(obj)
    return QuarantineOut.model_validate(obj)
