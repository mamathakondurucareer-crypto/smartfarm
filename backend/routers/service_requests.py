"""Service requests router — maintenance, repair, installation, etc."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.service_request import ServiceRequest
from backend.models.user import User, Employee
from backend.routers.auth import get_current_user
from backend.schemas import (
    ServiceRequestCreate, ServiceRequestOut,
    ServiceRequestUpdate, ServiceRequestAssign, ServiceRequestResolve,
)

router = APIRouter(prefix="/api/service-requests", tags=["Service Requests"])

ADMIN_ROLES = ("admin", "manager", "store_manager")


def _request_code(db: Session) -> str:
    count = db.query(ServiceRequest).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"SRQ-{ts}-{count + 1:04d}"


@router.get("", response_model=List[ServiceRequestOut])
def list_service_requests(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    requested_by: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ServiceRequest)
    if status:
        q = q.filter(ServiceRequest.status == status)
    if priority:
        q = q.filter(ServiceRequest.priority == priority)
    if department:
        q = q.filter(ServiceRequest.department == department)
    if category:
        q = q.filter(ServiceRequest.category == category)
    if assigned_to:
        q = q.filter(ServiceRequest.assigned_to == assigned_to)
    if requested_by:
        q = q.filter(ServiceRequest.requested_by == requested_by)
    return q.order_by(ServiceRequest.created_at.desc()).limit(limit).all()


@router.post("", response_model=ServiceRequestOut, status_code=201)
def create_service_request(
    data: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any authenticated user can raise a service request."""
    req = ServiceRequest(
        request_code=_request_code(db),
        requested_by=current_user.id,
        status="open",
        **data.model_dump(),
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/{request_id}", response_model=ServiceRequestOut)
def get_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Service request not found")
    return req


@router.put("/{request_id}", response_model=ServiceRequestOut)
def update_service_request(
    request_id: int,
    data: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Service request not found")

    # Only the requester or an admin can update
    if req.requested_by != current_user.id and current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Not authorised to update this request")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(req, field, value)
    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/assign", response_model=ServiceRequestOut)
def assign_service_request(
    request_id: int,
    data: ServiceRequestAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or manager role required")
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Service request not found")
    if not db.query(Employee).filter(Employee.id == data.assigned_to).first():
        raise HTTPException(404, "Employee not found")

    req.assigned_to = data.assigned_to
    if data.scheduled_date:
        req.scheduled_date = data.scheduled_date
    req.status = "assigned"
    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/resolve", response_model=ServiceRequestOut)
def resolve_service_request(
    request_id: int,
    data: ServiceRequestResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Service request not found")

    # Only assigned employee (via user link) or admin/manager can resolve
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    is_assigned_employee = emp and req.assigned_to == emp.id
    if not is_assigned_employee and current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Only the assigned employee or an admin/manager can resolve this request")

    if req.status in ("resolved", "closed"):
        raise HTTPException(400, f"Request is already '{req.status}'")

    req.status = "resolved"
    req.resolution_notes = data.resolution_notes
    req.actual_cost = data.actual_cost
    req.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return req
