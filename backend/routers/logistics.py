"""Logistics: delivery routes and trips router."""
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models.logistics import DeliveryRoute, DeliveryTrip, DeliveryTripOrder
from backend.models.market import CustomerOrder
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.activity_log_service import log_activity
from backend.schemas import (
    DeliveryRouteCreate, DeliveryRouteOut,
    DeliveryTripCreate, DeliveryTripOut,
    TripStatusUpdate, DeliveryConfirm, TripOrderAdd,
)

router = APIRouter(prefix="/api/logistics", tags=["Logistics"])

LOGISTICS_ROLES = ("admin", "manager", "store_manager", "driver", "supervisor")
ADMIN_ROLES = ("admin", "manager", "store_manager")


def _trip_code(db: Session) -> str:
    count = db.query(DeliveryTrip).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TRIP-{ts}-{count + 1:04d}"


# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

@router.get("/routes", response_model=List[DeliveryRouteOut])
def list_routes(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(DeliveryRoute)
    if is_active is not None:
        q = q.filter(DeliveryRoute.is_active == is_active)
    return q.order_by(DeliveryRoute.route_name).all()


@router.post("/routes", response_model=DeliveryRouteOut, status_code=201)
def create_route(
    data: DeliveryRouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or manager role required")
    if db.query(DeliveryRoute).filter(DeliveryRoute.route_code == data.route_code).first():
        raise HTTPException(400, f"Route code '{data.route_code}' already exists")
    route = DeliveryRoute(**data.model_dump())
    db.add(route)
    log_activity(db, "CREATE_ROUTE", "logistics", username=current_user.username,
                 user_id=current_user.id, entity_type="DeliveryRoute",
                 description=f"Route '{data.route_name}' ({data.route_code}) created")
    db.commit()
    db.refresh(route)
    return route


@router.get("/routes/{route_id}", response_model=DeliveryRouteOut)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    route = db.query(DeliveryRoute).filter(DeliveryRoute.id == route_id).first()
    if not route:
        raise HTTPException(404, "Route not found")
    return route


# ═══════════════════════════════════════════════════════════════
# TRIPS
# ═══════════════════════════════════════════════════════════════

@router.get("/trips", response_model=List[DeliveryTripOut])
def list_trips(
    status: Optional[str] = Query(None),
    driver_id: Optional[int] = Query(None),
    route_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(DeliveryTrip)
    if status:
        q = q.filter(DeliveryTrip.status == status)
    if driver_id:
        q = q.filter(DeliveryTrip.driver_id == driver_id)
    if route_id:
        q = q.filter(DeliveryTrip.route_id == route_id)
    if start_date:
        q = q.filter(DeliveryTrip.planned_departure >= start_date)
    if end_date:
        q = q.filter(DeliveryTrip.planned_departure <= end_date)
    return q.order_by(DeliveryTrip.planned_departure.desc()).limit(limit).all()


@router.post("/trips", response_model=DeliveryTripOut, status_code=201)
def create_trip(
    data: DeliveryTripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or manager role required")
    if data.route_id:
        if not db.query(DeliveryRoute).filter(DeliveryRoute.id == data.route_id).first():
            raise HTTPException(404, "Route not found")
    trip = DeliveryTrip(
        trip_code=_trip_code(db),
        **data.model_dump(),
    )
    db.add(trip)
    log_activity(db, "CREATE_TRIP", "logistics", username=current_user.username,
                 user_id=current_user.id, entity_type="DeliveryTrip",
                 description=f"Delivery trip created by '{current_user.username}'")
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/trips/active", response_model=List[DeliveryTripOut])
def get_active_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return trips currently in loading or in_transit state for the calling driver."""
    from backend.models.user import Employee
    emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not emp:
        raise HTTPException(404, "No employee record linked to your user account")
    trips = (
        db.query(DeliveryTrip)
        .filter(
            DeliveryTrip.driver_id == emp.id,
            DeliveryTrip.status.in_(["loading", "in_transit"]),
        )
        .all()
    )
    return trips


@router.get("/trips/{trip_id}", response_model=dict)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(DeliveryTrip)
        .options(joinedload(DeliveryTrip.trip_orders))
        .filter(DeliveryTrip.id == trip_id)
        .first()
    )
    if not trip:
        raise HTTPException(404, "Trip not found")
    return {
        "id": trip.id,
        "trip_code": trip.trip_code,
        "route_id": trip.route_id,
        "driver_id": trip.driver_id,
        "vehicle_number": trip.vehicle_number,
        "vehicle_type": trip.vehicle_type,
        "planned_departure": trip.planned_departure,
        "actual_departure": trip.actual_departure,
        "actual_arrival": trip.actual_arrival,
        "total_distance_km": trip.total_distance_km,
        "fuel_used_litres": trip.fuel_used_litres,
        "fuel_cost": trip.fuel_cost,
        "status": trip.status,
        "notes": trip.notes,
        "created_at": trip.created_at,
        "orders": [
            {
                "id": o.id,
                "order_id": o.order_id,
                "sequence_no": o.sequence_no,
                "delivery_address": o.delivery_address,
                "delivery_status": o.delivery_status,
                "delivery_time": o.delivery_time,
                "recipient_name": o.recipient_name,
            }
            for o in trip.trip_orders
        ],
    }


@router.put("/trips/{trip_id}/status", response_model=DeliveryTripOut)
def update_trip_status(
    trip_id: int,
    data: TripStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in LOGISTICS_ROLES:
        raise HTTPException(403, "Logistics role required")
    trip = db.query(DeliveryTrip).filter(DeliveryTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")

    valid_transitions = {
        "scheduled": ["loading", "returned"],
        "loading": ["in_transit", "returned"],
        "in_transit": ["delivered", "returned"],
        "delivered": [],
        "returned": [],
    }
    allowed = valid_transitions.get(trip.status, [])
    if data.status not in allowed and data.status != trip.status:
        raise HTTPException(400, f"Cannot transition from '{trip.status}' to '{data.status}'")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(trip, field, value)
    log_activity(db, "UPDATE_TRIP_STATUS", "logistics", username=current_user.username,
                 user_id=current_user.id, entity_type="DeliveryTrip", entity_id=trip_id,
                 description=f"Trip #{trip_id} status changed to '{data.status}' by '{current_user.username}'")
    db.commit()
    db.refresh(trip)
    return trip


@router.post("/trips/{trip_id}/orders")
def add_order_to_trip(
    trip_id: int,
    data: TripOrderAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or manager role required")
    trip = db.query(DeliveryTrip).filter(DeliveryTrip.id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    if trip.status not in ("scheduled", "loading"):
        raise HTTPException(400, "Cannot add orders to a trip that has already departed")

    order = db.query(CustomerOrder).filter(CustomerOrder.id == data.order_id).first()
    if not order:
        raise HTTPException(404, "Customer order not found")

    existing = (
        db.query(DeliveryTripOrder)
        .filter(
            DeliveryTripOrder.trip_id == trip_id,
            DeliveryTripOrder.order_id == data.order_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(400, "Order already assigned to this trip")

    trip_order = DeliveryTripOrder(
        trip_id=trip_id,
        order_id=data.order_id,
        sequence_no=data.sequence_no,
        delivery_address=data.delivery_address,
        delivery_status="pending",
    )
    db.add(trip_order)
    db.commit()
    return {"message": "Order added to trip", "trip_id": trip_id, "order_id": data.order_id}


@router.put("/trips/{trip_id}/orders/{order_id}/deliver")
def mark_order_delivered(
    trip_id: int,
    order_id: int,
    data: DeliveryConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in LOGISTICS_ROLES:
        raise HTTPException(403, "Logistics role required")
    trip_order = (
        db.query(DeliveryTripOrder)
        .filter(
            DeliveryTripOrder.trip_id == trip_id,
            DeliveryTripOrder.order_id == order_id,
        )
        .first()
    )
    if not trip_order:
        raise HTTPException(404, "Trip-order assignment not found")
    if trip_order.delivery_status == "delivered":
        raise HTTPException(400, "Order already marked as delivered")

    trip_order.delivery_status = "delivered"
    trip_order.delivery_time = datetime.now(timezone.utc)
    if data.recipient_name:
        trip_order.recipient_name = data.recipient_name
    if data.notes:
        trip_order.notes = data.notes

    # Update customer order status
    cust_order = db.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
    if cust_order:
        cust_order.order_status = "delivered"

    db.commit()
    return {"message": "Order marked as delivered", "trip_id": trip_id, "order_id": order_id}
