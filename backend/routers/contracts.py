"""Contract Farming & Consulting module — contracts, service logs, invoices."""

from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.contracts import (
    NeighbouringFarm, ConsultingContract, ServiceDeliveryLog, ConsultingInvoice,
)
from backend.schemas import (
    NeighbouringFarmCreate, NeighbouringFarmOut,
    ConsultingContractCreate, ConsultingContractOut,
    ServiceDeliveryLogCreate, ServiceDeliveryLogOut,
    ConsultingInvoiceCreate, ConsultingInvoiceOut,
)

router = APIRouter(prefix="/api/contracts", tags=["Contract Farming & Consulting"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Neighbouring Farms ────────────────────────────────────────────────────────

@router.post("/farms", response_model=NeighbouringFarmOut)
def create_farm(
    data: NeighbouringFarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = NeighbouringFarm(**data.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/farms", response_model=list[NeighbouringFarmOut])
def list_farms(
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(NeighbouringFarm)
    if district:
        q = q.filter(NeighbouringFarm.district.ilike(f"%{district}%"))
    return q.order_by(NeighbouringFarm.farm_name).all()


# ── Contracts ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=ConsultingContractOut)
def create_contract(
    data: ConsultingContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    contract = ConsultingContract(**data.model_dump(), created_by=current_user.id)
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/", response_model=list[ConsultingContractOut])
def list_contracts(
    status: Optional[str] = None,
    contract_type: Optional[str] = None,
    neighbouring_farm_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ConsultingContract)
    if status:
        q = q.filter(ConsultingContract.status == status)
    if contract_type:
        q = q.filter(ConsultingContract.contract_type == contract_type)
    if neighbouring_farm_id:
        q = q.filter(ConsultingContract.neighbouring_farm_id == neighbouring_farm_id)
    return q.order_by(ConsultingContract.start_date.desc()).all()


@router.get("/{contract_id}", response_model=ConsultingContractOut)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = db.query(ConsultingContract).filter(ConsultingContract.id == contract_id).first()
    if not c:
        raise HTTPException(404, "Contract not found")
    return c


@router.put("/{contract_id}/status")
def update_contract_status(
    contract_id: int,
    status: str = Query(..., description="active | completed | terminated"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    if status not in ("active", "completed", "terminated", "draft"):
        raise HTTPException(400, "Invalid status")
    c = db.query(ConsultingContract).filter(ConsultingContract.id == contract_id).first()
    if not c:
        raise HTTPException(404, "Contract not found")
    c.status = status
    db.commit()
    return {"id": contract_id, "status": status}


# ── Service Delivery Logs ─────────────────────────────────────────────────────

@router.post("/service-logs", response_model=ServiceDeliveryLogOut)
def log_service_delivery(
    data: ServiceDeliveryLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = ServiceDeliveryLog(**data.model_dump(), delivered_by=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/service-logs/{contract_id}", response_model=list[ServiceDeliveryLogOut])
def list_service_logs(
    contract_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ServiceDeliveryLog).filter(ServiceDeliveryLog.contract_id == contract_id)
    if date_from:
        q = q.filter(ServiceDeliveryLog.service_date >= date_from)
    if date_to:
        q = q.filter(ServiceDeliveryLog.service_date <= date_to)
    return q.order_by(ServiceDeliveryLog.service_date.desc()).all()


# ── Invoices ──────────────────────────────────────────────────────────────────

@router.post("/invoices", response_model=ConsultingInvoiceOut)
def create_invoice(
    data: ConsultingInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    inv = ConsultingInvoice(**data.model_dump(), created_by=current_user.id)
    db.add(inv)

    # Update contract total_billed
    contract = db.query(ConsultingContract).filter(ConsultingContract.id == data.contract_id).first()
    if contract:
        contract.total_billed = round(contract.total_billed + inv.total_amount, 2)

    db.commit()
    db.refresh(inv)
    return inv


@router.get("/invoices/{contract_id}", response_model=list[ConsultingInvoiceOut])
def list_invoices(
    contract_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ConsultingInvoice).filter(ConsultingInvoice.contract_id == contract_id)
    if status:
        q = q.filter(ConsultingInvoice.status == status)
    return q.order_by(ConsultingInvoice.invoice_date.desc()).all()


@router.patch("/invoices/{invoice_id}/pay")
def record_invoice_payment(
    invoice_id: int,
    amount: float = Query(..., gt=0),
    payment_mode: str = Query(default="bank_transfer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(ConsultingInvoice).filter(ConsultingInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(404, "Invoice not found")
    inv.amount_received = round(inv.amount_received + amount, 2)
    inv.payment_mode = payment_mode
    inv.payment_date = date.today()
    if inv.amount_received >= inv.total_amount:
        inv.status = "paid"
    elif inv.amount_received > 0:
        inv.status = "partial"

    # Update contract total_received
    contract = db.query(ConsultingContract).filter(ConsultingContract.id == inv.contract_id).first()
    if contract:
        contract.total_received = round(contract.total_received + amount, 2)

    db.commit()
    return {"invoice_id": invoice_id, "status": inv.status, "amount_received": inv.amount_received}


# ── Revenue Analytics ─────────────────────────────────────────────────────────

@router.get("/analytics/revenue")
def revenue_by_contract(
    year: int = Query(default=2025),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revenue summary by contract with active vs completed breakdown."""
    contracts = db.query(ConsultingContract).all()

    active = [c for c in contracts if c.status == "active"]
    completed = [c for c in contracts if c.status == "completed"]

    total_billed = round(sum(c.total_billed for c in contracts), 2)
    total_received = round(sum(c.total_received for c in contracts), 2)

    by_type: dict = {}
    for c in contracts:
        by_type[c.contract_type] = by_type.get(c.contract_type, 0) + c.total_billed

    return {
        "year": year,
        "total_contracts": len(contracts),
        "active_contracts": len(active),
        "completed_contracts": len(completed),
        "total_billed": total_billed,
        "total_received": total_received,
        "outstanding": round(total_billed - total_received, 2),
        "annual_target": 8000000,  # ₹80 Lakh target
        "achievement_pct": round(total_received / 8000000 * 100, 1) if total_received else 0.0,
        "revenue_by_type": {k: round(v, 2) for k, v in by_type.items()},
        "contracts_detail": [
            {
                "id": c.id,
                "contract_number": c.contract_number,
                "client_name": c.client_name,
                "contract_type": c.contract_type,
                "status": c.status,
                "contract_value": c.contract_value,
                "total_billed": c.total_billed,
                "total_received": c.total_received,
            }
            for c in contracts
        ],
    }
