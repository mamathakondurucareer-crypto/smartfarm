"""Agri-Tourism / Farm Visit module — packages, bookings, visitor groups, revenue."""

from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.agritourism import VisitPackage, VisitorGroup, VisitBooking, TourRevenueEntry
from backend.schemas import (
    VisitPackageCreate, VisitPackageOut,
    VisitorGroupCreate, VisitorGroupOut,
    VisitBookingCreate, VisitBookingOut,
    TourRevenueEntryCreate, TourRevenueEntryOut,
)

router = APIRouter(prefix="/api/agritourism", tags=["Agri-Tourism"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Visit Packages ────────────────────────────────────────────────────────────

@router.post("/packages", response_model=VisitPackageOut)
def create_package(
    data: VisitPackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    pkg = VisitPackage(**data.model_dump())
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    return pkg


@router.get("/packages", response_model=list[VisitPackageOut])
def list_packages(
    active_only: bool = True,
    package_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(VisitPackage)
    if active_only:
        q = q.filter(VisitPackage.is_active == True)
    if package_type:
        q = q.filter(VisitPackage.package_type == package_type)
    return q.order_by(VisitPackage.name).all()


@router.put("/packages/{pkg_id}", response_model=VisitPackageOut)
def update_package(
    pkg_id: int,
    data: VisitPackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    pkg = db.query(VisitPackage).filter(VisitPackage.id == pkg_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")
    for k, v in data.model_dump().items():
        setattr(pkg, k, v)
    db.commit()
    db.refresh(pkg)
    return pkg


# ── Visitor Groups ────────────────────────────────────────────────────────────

@router.post("/visitor-groups", response_model=VisitorGroupOut)
def create_visitor_group(
    data: VisitorGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vg = VisitorGroup(**data.model_dump())
    db.add(vg)
    db.commit()
    db.refresh(vg)
    return vg


@router.get("/visitor-groups", response_model=list[VisitorGroupOut])
def list_visitor_groups(
    group_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(VisitorGroup)
    if group_type:
        q = q.filter(VisitorGroup.group_type == group_type)
    return q.order_by(VisitorGroup.group_name).all()


# ── Bookings ──────────────────────────────────────────────────────────────────

@router.post("/bookings", response_model=VisitBookingOut)
def create_booking(
    data: VisitBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pkg = db.query(VisitPackage).filter(VisitPackage.id == data.package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")

    total = round(pkg.price_per_person * data.pax_count, 2)
    balance = round(total - data.advance_paid, 2)

    booking = VisitBooking(
        **data.model_dump(exclude={"total_amount", "balance_due", "price_per_person"}),
        price_per_person=pkg.price_per_person,
        total_amount=total,
        balance_due=balance,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/bookings", response_model=list[VisitBookingOut])
def list_bookings(
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    package_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(VisitBooking)
    if status:
        q = q.filter(VisitBooking.status == status)
    if package_id:
        q = q.filter(VisitBooking.package_id == package_id)
    if date_from:
        q = q.filter(VisitBooking.visit_date >= date_from)
    if date_to:
        q = q.filter(VisitBooking.visit_date <= date_to)
    return q.order_by(VisitBooking.visit_date.desc()).all()


@router.get("/bookings/availability")
def check_availability(
    visit_date: date = Query(...),
    package_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return booked slots and remaining capacity for a given date and package."""
    pkg = db.query(VisitPackage).filter(VisitPackage.id == package_id).first()
    if not pkg:
        raise HTTPException(404, "Package not found")

    bookings = db.query(VisitBooking).filter(
        VisitBooking.package_id == package_id,
        VisitBooking.visit_date == visit_date,
        VisitBooking.status.in_(["pending", "confirmed"]),
    ).all()

    booked_slots = [b.time_slot for b in bookings]
    booked_pax = sum(b.pax_count for b in bookings)
    return {
        "package_id": package_id,
        "visit_date": visit_date.isoformat(),
        "max_group_size": pkg.max_group_size,
        "slots_per_day": pkg.slots_per_day,
        "booked_slots": booked_slots,
        "booked_pax": booked_pax,
        "remaining_capacity": max(0, pkg.max_group_size * pkg.slots_per_day - booked_pax),
    }


@router.put("/bookings/{booking_id}/confirm")
def confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    booking = db.query(VisitBooking).filter(VisitBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    booking.status = "confirmed"
    booking.confirmed_by = current_user.id
    db.commit()
    return {"id": booking_id, "status": "confirmed"}


@router.put("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    booking = db.query(VisitBooking).filter(VisitBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    booking.status = "cancelled"
    db.commit()
    return {"id": booking_id, "status": "cancelled"}


@router.put("/bookings/{booking_id}/complete")
def complete_booking(
    booking_id: int,
    feedback_rating: Optional[int] = Query(default=None, ge=1, le=5),
    feedback_comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(VisitBooking).filter(VisitBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    booking.status = "completed"
    if feedback_rating is not None:
        booking.feedback_rating = feedback_rating
    if feedback_comment:
        booking.feedback_comment = feedback_comment
    db.commit()
    return {"id": booking_id, "status": "completed"}


# ── Revenue ───────────────────────────────────────────────────────────────────

@router.post("/revenue", response_model=TourRevenueEntryOut)
def record_revenue(
    data: TourRevenueEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = TourRevenueEntry(**data.model_dump(), received_by=current_user.id)
    db.add(entry)

    # Update booking balance
    booking = db.query(VisitBooking).filter(VisitBooking.id == data.booking_id).first()
    if booking:
        booking.advance_paid = round(booking.advance_paid + data.amount_received, 2)
        booking.balance_due = max(0.0, round(booking.total_amount - booking.advance_paid, 2))

    db.commit()
    db.refresh(entry)
    return entry


@router.get("/revenue/monthly")
def revenue_by_month(
    year: int = Query(default=2025),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Monthly tour revenue aggregation."""
    entries = db.query(TourRevenueEntry).filter(
        func.extract("year", TourRevenueEntry.entry_date) == year
    ).all()

    monthly: dict = {}
    for e in entries:
        m = e.entry_date.month
        monthly[m] = round(monthly.get(m, 0.0) + e.amount_received, 2)

    total = round(sum(monthly.values()), 2)
    return {
        "year": year,
        "monthly": {str(m): v for m, v in sorted(monthly.items())},
        "total": total,
        "annual_target": 1500000,  # ₹15 Lakh target
        "achievement_pct": round(total / 1500000 * 100, 1) if total else 0.0,
    }
