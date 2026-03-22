"""Government Subsidy Tracker — schemes, applications, disbursements."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.subsidies import SubsidyScheme, SubsidyApplication, DisbursementRecord
from backend.schemas import (
    SubsidySchemeCreate, SubsidySchemeOut,
    SubsidyApplicationCreate, SubsidyApplicationOut,
    DisbursementRecordCreate, DisbursementRecordOut,
)

router = APIRouter(prefix="/api/subsidies", tags=["Government Subsidies"])

_WRITE_ROLES = ("admin", "manager")


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Schemes ───────────────────────────────────────────────────────────────────

@router.get("/schemes", response_model=list[SubsidySchemeOut])
def list_schemes(
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SubsidyScheme)
    if active_only:
        q = q.filter(SubsidyScheme.is_active == True)
    if category:
        q = q.filter(SubsidyScheme.category == category)
    return q.order_by(SubsidyScheme.scheme_code).all()


@router.post("/schemes", response_model=SubsidySchemeOut)
def create_scheme(
    data: SubsidySchemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    scheme = SubsidyScheme(**data.model_dump())
    db.add(scheme)
    try:
        db.commit()
        db.refresh(scheme)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "scheme_code already exists")
    return scheme


@router.get("/schemes/{scheme_id}", response_model=SubsidySchemeOut)
def get_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = db.query(SubsidyScheme).filter(SubsidyScheme.id == scheme_id).first()
    if not s:
        raise HTTPException(404, "Scheme not found")
    return s


# ── Applications ──────────────────────────────────────────────────────────────

@router.post("/applications", response_model=SubsidyApplicationOut)
def submit_application(
    data: SubsidyApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scheme = db.query(SubsidyScheme).filter(SubsidyScheme.id == data.scheme_id).first()
    if not scheme:
        raise HTTPException(404, "Scheme not found")
    app = SubsidyApplication(**data.model_dump(), submitted_by=current_user.id)
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("/applications", response_model=list[SubsidyApplicationOut])
def list_applications(
    status: Optional[str] = None,
    scheme_id: Optional[int] = None,
    date_from: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SubsidyApplication)
    if status:
        q = q.filter(SubsidyApplication.status == status)
    if scheme_id:
        q = q.filter(SubsidyApplication.scheme_id == scheme_id)
    if date_from:
        q = q.filter(SubsidyApplication.applied_date >= date_from)
    return q.order_by(SubsidyApplication.applied_date.desc()).all()


@router.patch("/applications/{app_id}/status")
def update_application_status(
    app_id: int,
    status: str = Query(...),
    approved_amount: Optional[float] = None,
    rejection_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    valid = {"submitted", "under_review", "approved", "rejected", "disbursed", "lapsed"}
    if status not in valid:
        raise HTTPException(400, f"status must be one of: {', '.join(sorted(valid))}")
    app = db.query(SubsidyApplication).filter(SubsidyApplication.id == app_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    app.status = status
    if approved_amount is not None:
        app.approved_amount = approved_amount
        app.approval_date = date.today()
    if rejection_reason:
        app.rejection_reason = rejection_reason
    db.commit()
    return {"id": app_id, "status": status}


# ── Disbursements ─────────────────────────────────────────────────────────────

@router.post("/disbursements", response_model=DisbursementRecordOut)
def record_disbursement(
    data: DisbursementRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = db.query(SubsidyApplication).filter(SubsidyApplication.id == data.application_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    if app.status not in ("approved", "disbursed"):
        raise HTTPException(400, "Application must be in approved or disbursed status")

    record = DisbursementRecord(**data.model_dump(), recorded_by=current_user.id)
    db.add(record)
    app.status = "disbursed"
    db.commit()
    db.refresh(record)
    return record


@router.get("/disbursements", response_model=list[DisbursementRecordOut])
def list_disbursements(
    application_id: Optional[int] = None,
    date_from: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(DisbursementRecord)
    if application_id:
        q = q.filter(DisbursementRecord.application_id == application_id)
    if date_from:
        q = q.filter(DisbursementRecord.disbursement_date >= date_from)
    return q.order_by(DisbursementRecord.disbursement_date.desc()).all()


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary")
def subsidy_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Total subsidy received vs pending by scheme category."""
    apps = db.query(SubsidyApplication).all()
    disbursements = db.query(DisbursementRecord).all()

    total_claimed = round(sum(a.claimed_subsidy_amount for a in apps), 2)
    total_approved = round(sum(a.approved_amount or 0 for a in apps if a.status in ("approved", "disbursed")), 2)
    total_received = round(sum(d.amount_received for d in disbursements), 2)
    pending = round(total_approved - total_received, 2)

    by_status: dict = {}
    for a in apps:
        by_status[a.status] = by_status.get(a.status, 0) + 1

    return {
        "total_applications": len(apps),
        "total_claimed": total_claimed,
        "total_approved": total_approved,
        "total_received": total_received,
        "pending_disbursement": max(0.0, pending),
        "by_status": by_status,
    }
