"""Compliance & Licence Tracker router."""
from datetime import date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.compliance import Licence, ComplianceTask

router = APIRouter(prefix="/api/compliance", tags=["Compliance & Licences"])
MGMT_ROLES = ("admin", "manager")

# ── Schemas ──────────────────────────────────────────────────────────────
class LicenceCreate(BaseModel):
    name: str
    category: str = ""
    issuing_authority: str
    licence_number: Optional[str] = None
    cost_inr: float = 0.0
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    status: str = "active"
    document_url: Optional[str] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None

class LicenceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    issuing_authority: Optional[str] = None
    licence_number: Optional[str] = None
    cost_inr: Optional[float] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    status: Optional[str] = None
    document_url: Optional[str] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None

class LicenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    issuing_authority: str
    licence_number: Optional[str]
    cost_inr: float
    issue_date: Optional[date]
    expiry_date: Optional[date]
    renewal_date: Optional[date]
    status: str
    document_url: Optional[str]
    responsible_person: Optional[str]
    notes: Optional[str]

class ComplianceTaskCreate(BaseModel):
    title: str
    task_type: str = ""
    frequency: str = "monthly"
    due_date: date
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class ComplianceTaskUpdate(BaseModel):
    title: Optional[str] = None
    task_type: Optional[str] = None
    frequency: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    completed: Optional[bool] = None
    completed_date: Optional[date] = None
    document_url: Optional[str] = None
    notes: Optional[str] = None

class ComplianceTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    task_type: str
    frequency: str
    due_date: date
    assigned_to: Optional[str]
    completed: bool
    completed_date: Optional[date]
    document_url: Optional[str]
    notes: Optional[str]

# ── Licences ─────────────────────────────────────────────────────────────
@router.get("/licences", response_model=List[LicenceOut])
def list_licences(status: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Auto-update expiry status
    today = date.today()
    for lic in db.query(Licence).all():
        if lic.expiry_date:
            days_left = (lic.expiry_date - today).days
            if days_left < 0:
                lic.status = "expired"
            elif days_left <= 30:
                lic.status = "expiring"
    db.commit()

    q = db.query(Licence)
    if status:
        q = q.filter(Licence.status == status)
    return q.order_by(Licence.expiry_date.asc().nulls_last()).all()

@router.post("/licences", response_model=LicenceOut, status_code=201)
def create_licence(data: LicenceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = Licence(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return LicenceOut.model_validate(obj)

@router.put("/licences/{lic_id}", response_model=LicenceOut)
def update_licence(lic_id: int, data: LicenceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = db.query(Licence).filter(Licence.id == lic_id).first()
    if not obj:
        raise HTTPException(404, "Licence not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return LicenceOut.model_validate(obj)

@router.delete("/licences/{lic_id}", status_code=204)
def delete_licence(lic_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in ("admin",):
        raise HTTPException(403, "Admin role required")
    obj = db.query(Licence).filter(Licence.id == lic_id).first()
    if not obj:
        raise HTTPException(404, "Licence not found")
    db.delete(obj)
    db.commit()

@router.get("/licences/expiring-soon")
def expiring_soon(days: int = 60, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    today = date.today()
    cutoff = today + timedelta(days=days)
    licences = db.query(Licence).filter(
        Licence.expiry_date != None,
        Licence.expiry_date >= today,
        Licence.expiry_date <= cutoff,
    ).order_by(Licence.expiry_date.asc()).all()
    return [{"id": l.id, "name": l.name, "expiry_date": str(l.expiry_date), "days_left": (l.expiry_date - today).days, "status": l.status} for l in licences]

# ── Compliance Tasks ──────────────────────────────────────────────────────
@router.get("/tasks", response_model=List[ComplianceTaskOut])
def list_tasks(completed: Optional[bool] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(ComplianceTask)
    if completed is not None:
        q = q.filter(ComplianceTask.completed == completed)
    return q.order_by(ComplianceTask.due_date.asc()).all()

@router.post("/tasks", response_model=ComplianceTaskOut, status_code=201)
def create_task(data: ComplianceTaskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name not in MGMT_ROLES:
        raise HTTPException(403, "Manager role required")
    obj = ComplianceTask(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ComplianceTaskOut.model_validate(obj)

@router.put("/tasks/{task_id}", response_model=ComplianceTaskOut)
def update_task(task_id: int, data: ComplianceTaskUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not obj:
        raise HTTPException(404, "Task not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return ComplianceTaskOut.model_validate(obj)

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not obj:
        raise HTTPException(404, "Task not found")
    db.delete(obj)
    db.commit()
