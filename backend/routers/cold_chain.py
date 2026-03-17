"""Cold-chain shipment tracking: vehicles, temperature logs, delivery confirmation, rejections."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models.logistics import (
    Vehicle, ColdChainShipment, ShipmentTemperatureLog,
    ShipmentDeliveryConfirmation, ShipmentRejection,
    COLD_CHAIN_THRESHOLDS,
)
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import (
    VehicleCreate, VehicleOut,
    ColdChainShipmentCreate, ColdChainShipmentOut,
    TemperatureLogCreate, TemperatureLogOut,
    DeliveryConfirmationCreate, DeliveryConfirmationOut,
    RejectionCreate, RejectionOut,
)

router = APIRouter(prefix="/api/cold-chain", tags=["Cold Chain"])

_WRITE_ROLES = ("admin", "manager", "supervisor", "driver", "operator")
_ADMIN_ROLES = ("admin", "manager", "supervisor")


def _shipment_code(db: Session) -> str:
    count = db.query(ColdChainShipment).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"SHP-{ts}-{count + 1:04d}"


def _temp_threshold(category: str) -> Optional[float]:
    return COLD_CHAIN_THRESHOLDS.get(category.lower())


# ═══════════════════════════════════════════════════════════════
# VEHICLES
# ═══════════════════════════════════════════════════════════════

@router.get("/vehicles", response_model=List[VehicleOut])
def list_vehicles(
    refrigerated_only: bool = Query(False),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Vehicle).filter(Vehicle.is_active == True)
    if refrigerated_only:
        q = q.filter(Vehicle.refrigerated == True)
    return q.order_by(Vehicle.vehicle_number).all()


@router.post("/vehicles", response_model=VehicleOut, status_code=201)
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _ADMIN_ROLES:
        raise HTTPException(403, "Manager role required")
    if db.query(Vehicle).filter(Vehicle.vehicle_number == data.vehicle_number).first():
        raise HTTPException(400, f"Vehicle '{data.vehicle_number}' already registered")
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.put("/vehicles/{vehicle_id}/deactivate")
def deactivate_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _ADMIN_ROLES:
        raise HTTPException(403, "Manager role required")
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    v.is_active = False
    db.commit()
    return {"message": f"Vehicle {v.vehicle_number} deactivated"}


# ═══════════════════════════════════════════════════════════════
# SHIPMENTS
# ═══════════════════════════════════════════════════════════════

@router.post("/shipments", response_model=ColdChainShipmentOut, status_code=201)
def create_shipment(
    data: ColdChainShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to create shipments")

    # Serialize product_lots to plain dicts for JSON column
    lots = (
        [lot.model_dump() for lot in data.product_lots]
        if data.product_lots
        else None
    )

    shipment = ColdChainShipment(
        shipment_code=_shipment_code(db),
        vehicle_id=data.vehicle_id,
        driver_employee_id=data.driver_employee_id,
        origin_city=data.origin_city,
        destination_city=data.destination_city,
        delivery_address=data.delivery_address,
        product_category=data.product_category,
        product_lots=lots,
        total_weight_kg=data.total_weight_kg,
        required_temp_min_c=data.required_temp_min_c,
        required_temp_max_c=data.required_temp_max_c,
        dispatch_time=data.dispatch_time,
        eta=data.eta,
        notes=data.notes,
        status="scheduled",
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/shipments", response_model=List[ColdChainShipmentOut])
def list_shipments(
    status: Optional[str] = Query(None),
    destination_city: Optional[str] = Query(None),
    product_category: Optional[str] = Query(None),
    has_breach: Optional[bool] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ColdChainShipment)
    if status:
        q = q.filter(ColdChainShipment.status == status)
    if destination_city:
        q = q.filter(ColdChainShipment.destination_city.ilike(f"%{destination_city}%"))
    if product_category:
        q = q.filter(ColdChainShipment.product_category == product_category)
    if has_breach is not None:
        q = q.filter(ColdChainShipment.has_temperature_breach == has_breach)
    if from_date:
        q = q.filter(ColdChainShipment.dispatch_time >= from_date)
    if to_date:
        q = q.filter(ColdChainShipment.dispatch_time <= to_date)
    return q.order_by(ColdChainShipment.created_at.desc()).limit(limit).all()


@router.get("/shipments/{shipment_id}")
def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    shipment = (
        db.query(ColdChainShipment)
        .options(
            joinedload(ColdChainShipment.temperature_logs),
            joinedload(ColdChainShipment.delivery_confirmation),
            joinedload(ColdChainShipment.rejections),
        )
        .filter(ColdChainShipment.id == shipment_id)
        .first()
    )
    if not shipment:
        raise HTTPException(404, "Shipment not found")

    return {
        "shipment": ColdChainShipmentOut.model_validate(shipment),
        "temperature_logs": [TemperatureLogOut.model_validate(t) for t in shipment.temperature_logs],
        "delivery_confirmation": (
            DeliveryConfirmationOut.model_validate(shipment.delivery_confirmation)
            if shipment.delivery_confirmation else None
        ),
        "rejections": [RejectionOut.model_validate(r) for r in shipment.rejections],
    }


@router.put("/shipments/{shipment_id}/dispatch")
def dispatch_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role")
    s = db.query(ColdChainShipment).filter(ColdChainShipment.id == shipment_id).first()
    if not s:
        raise HTTPException(404, "Shipment not found")
    if s.status != "scheduled":
        raise HTTPException(400, f"Cannot dispatch a shipment with status '{s.status}'")
    s.status = "dispatched"
    s.dispatch_time = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Shipment dispatched", "shipment_code": s.shipment_code}


# ═══════════════════════════════════════════════════════════════
# TEMPERATURE LOGGING
# ═══════════════════════════════════════════════════════════════

@router.post("/shipments/{shipment_id}/temperature", response_model=TemperatureLogOut, status_code=201)
def log_temperature(
    shipment_id: int,
    data: TemperatureLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role")
    shipment = db.query(ColdChainShipment).filter(ColdChainShipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(404, "Shipment not found")
    if shipment.status in ("delivered", "fully_rejected"):
        raise HTTPException(400, "Cannot log temperature for a completed shipment")

    threshold = _temp_threshold(shipment.product_category)
    is_breach = threshold is not None and data.temperature_c > threshold

    log = ShipmentTemperatureLog(
        shipment_id=shipment_id,
        recorded_at=datetime.now(timezone.utc),
        temperature_c=data.temperature_c,
        humidity_pct=data.humidity_pct,
        location=data.location,
        is_breach=is_breach,
        breach_threshold_c=threshold if is_breach else None,
        recorded_by=data.recorded_by,
    )
    db.add(log)

    # Mark shipment as having a breach (sticky flag — never cleared once set)
    if is_breach and not shipment.has_temperature_breach:
        shipment.has_temperature_breach = True

    # Auto-advance status to in_transit on first reading
    if shipment.status == "dispatched":
        shipment.status = "in_transit"

    db.commit()
    db.refresh(log)
    return log


@router.get("/shipments/{shipment_id}/temperature", response_model=List[TemperatureLogOut])
def get_temperature_logs(
    shipment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(ColdChainShipment).filter(ColdChainShipment.id == shipment_id).first():
        raise HTTPException(404, "Shipment not found")
    return (
        db.query(ShipmentTemperatureLog)
        .filter(ShipmentTemperatureLog.shipment_id == shipment_id)
        .order_by(ShipmentTemperatureLog.recorded_at)
        .all()
    )


# ═══════════════════════════════════════════════════════════════
# DELIVERY CONFIRMATION
# ═══════════════════════════════════════════════════════════════

@router.post("/shipments/{shipment_id}/confirm-delivery", response_model=DeliveryConfirmationOut, status_code=201)
def confirm_delivery(
    shipment_id: int,
    data: DeliveryConfirmationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role")
    shipment = db.query(ColdChainShipment).filter(ColdChainShipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(404, "Shipment not found")
    if shipment.status in ("delivered", "fully_rejected"):
        raise HTTPException(400, f"Shipment already finalised (status: {shipment.status})")
    if shipment.delivery_confirmation:
        raise HTTPException(400, "Delivery already confirmed for this shipment")

    # Check temperature compliance at delivery
    threshold = _temp_threshold(shipment.product_category)
    is_compliant = True
    if data.temperature_at_delivery_c is not None and threshold is not None:
        is_compliant = data.temperature_at_delivery_c <= threshold

    confirmation = ShipmentDeliveryConfirmation(
        shipment_id=shipment_id,
        confirmed_at=datetime.now(timezone.utc),
        recipient_name=data.recipient_name,
        recipient_phone=data.recipient_phone,
        photo_url=data.photo_url,
        delivered_weight_kg=data.delivered_weight_kg,
        temperature_at_delivery_c=data.temperature_at_delivery_c,
        is_temperature_compliant=is_compliant,
        confirmed_by_user_id=current_user.id,
        notes=data.notes,
    )
    db.add(confirmation)

    shipment.actual_arrival = datetime.now(timezone.utc)
    shipment.status = "delivered"
    if data.temperature_at_delivery_c is not None and not is_compliant:
        shipment.has_temperature_breach = True

    db.commit()
    db.refresh(confirmation)
    return confirmation


# ═══════════════════════════════════════════════════════════════
# REJECTION / CREDIT NOTE
# ═══════════════════════════════════════════════════════════════

@router.post("/shipments/{shipment_id}/reject", response_model=RejectionOut, status_code=201)
def record_rejection(
    shipment_id: int,
    data: RejectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role")
    shipment = db.query(ColdChainShipment).filter(ColdChainShipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(404, "Shipment not found")
    if shipment.status == "fully_rejected":
        raise HTTPException(400, "Shipment already fully rejected")

    if data.rejected_quantity_kg <= 0:
        raise HTTPException(400, "rejected_quantity_kg must be > 0")
    if data.accepted_quantity_kg < 0:
        raise HTTPException(400, "accepted_quantity_kg cannot be negative")

    rejection = ShipmentRejection(
        shipment_id=shipment_id,
        rejected_at=datetime.now(timezone.utc),
        rejection_reason=data.rejection_reason,
        rejected_quantity_kg=data.rejected_quantity_kg,
        accepted_quantity_kg=data.accepted_quantity_kg,
        credit_note_number=data.credit_note_number,
        credit_note_amount=data.credit_note_amount,
        photo_url=data.photo_url,
        customer_name=data.customer_name,
        raised_by_user_id=current_user.id,
        notes=data.notes,
    )
    db.add(rejection)

    # Update shipment status based on how much was accepted
    if data.accepted_quantity_kg == 0:
        shipment.status = "fully_rejected"
    else:
        shipment.status = "partially_rejected"

    shipment.actual_arrival = shipment.actual_arrival or datetime.now(timezone.utc)
    db.commit()
    db.refresh(rejection)
    return rejection


@router.get("/shipments/{shipment_id}/rejections", response_model=List[RejectionOut])
def list_rejections(
    shipment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(ColdChainShipment).filter(ColdChainShipment.id == shipment_id).first():
        raise HTTPException(404, "Shipment not found")
    return (
        db.query(ShipmentRejection)
        .filter(ShipmentRejection.shipment_id == shipment_id)
        .order_by(ShipmentRejection.rejected_at)
        .all()
    )


# ═══════════════════════════════════════════════════════════════
# SUMMARY / ANALYTICS
# ═══════════════════════════════════════════════════════════════

@router.get("/summary")
def cold_chain_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """KPI summary: total shipments, breach rate, rejection rate, city breakdown."""
    from datetime import timedelta
    from sqlalchemy import func
    since = datetime.now(timezone.utc) - timedelta(days=days)

    total = db.query(func.count(ColdChainShipment.id)).filter(
        ColdChainShipment.created_at >= since
    ).scalar() or 0

    breached = db.query(func.count(ColdChainShipment.id)).filter(
        ColdChainShipment.created_at >= since,
        ColdChainShipment.has_temperature_breach == True,
    ).scalar() or 0

    rejected = db.query(func.count(ColdChainShipment.id)).filter(
        ColdChainShipment.created_at >= since,
        ColdChainShipment.status.in_(["partially_rejected", "fully_rejected"]),
    ).scalar() or 0

    # Per-city breakdown
    city_rows = (
        db.query(
            ColdChainShipment.destination_city,
            func.count(ColdChainShipment.id).label("count"),
            func.sum(ColdChainShipment.total_weight_kg).label("total_kg"),
        )
        .filter(ColdChainShipment.created_at >= since)
        .group_by(ColdChainShipment.destination_city)
        .all()
    )

    return {
        "period_days": days,
        "total_shipments": total,
        "temperature_breach_count": breached,
        "breach_rate_pct": round(breached / total * 100, 1) if total else 0,
        "rejection_count": rejected,
        "rejection_rate_pct": round(rejected / total * 100, 1) if total else 0,
        "by_city": [
            {
                "city": r.destination_city,
                "shipment_count": r.count,
                "total_kg": round(r.total_kg or 0, 1),
            }
            for r in city_rows
        ],
    }
