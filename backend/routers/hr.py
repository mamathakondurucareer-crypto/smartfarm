"""HR & Payroll — leave, attendance, payroll auto-computation, performance, training."""

from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import (
    User, Employee, Attendance, LeaveRequest, LeaveBalance,
    PayrollRun, PerformanceReview, TrainingRecord,
)
from backend.schemas import (
    LeaveRequestCreate, LeaveRequestOut, LeaveApprovalUpdate,
    AttendanceCreate, AttendanceOut, LeaveBalanceOut,
    PayrollRunCreate, PayrollRunOut,
    PerformanceReviewCreate, PerformanceReviewOut,
    TrainingRecordCreate, TrainingRecordOut,
)

router = APIRouter(prefix="/api/hr", tags=["HR & Payroll"])

_WRITE_ROLES = ("admin", "manager", "supervisor")
_PAYROLL_ROLES = ("admin", "manager")

HOURLY_OT_MULTIPLIER = 2.0
WORKING_DAYS_PER_MONTH = 26


# ── Helpers ─────────────────────────────────────────────────────────────────

def _require_write(current_user: User):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient permissions")


def _get_employee_or_404(db: Session, employee_id: int) -> Employee:
    emp = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.deleted_at.is_(None),
    ).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp


def _get_current_employee(db: Session, current_user: User) -> Optional[Employee]:
    """Return the Employee record linked to current_user, or None."""
    return db.query(Employee).filter(
        Employee.user_id == current_user.id,
        Employee.deleted_at.is_(None),
    ).first()


def _own_employee_id(db: Session, current_user: User) -> Optional[int]:
    """Return employee_id for current_user if they have an employee record."""
    emp = _get_current_employee(db, current_user)
    return emp.id if emp else None


# ── Leave Requests ───────────────────────────────────────────────────────────

@router.post("/leave-requests", response_model=LeaveRequestOut)
def create_leave_request(
    data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_employee_or_404(db, data.employee_id)
    req = LeaveRequest(**data.model_dump())
    req.status = "pending"
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/leave-requests", response_model=list[LeaveRequestOut])
def list_leave_requests(
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(LeaveRequest)
    # Non-management users can only see their own leave requests
    if current_user.role.name not in _WRITE_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id is None:
            return []
        q = q.filter(LeaveRequest.employee_id == own_id)
    elif employee_id:
        q = q.filter(LeaveRequest.employee_id == employee_id)
    if status:
        q = q.filter(LeaveRequest.status == status)
    return q.order_by(LeaveRequest.start_date.desc()).all()


@router.put("/leave-requests/{request_id}/approve", response_model=LeaveRequestOut)
def approve_or_reject_leave(
    request_id: int,
    data: LeaveApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    if data.status not in ("approved", "rejected"):
        raise HTTPException(400, "status must be 'approved' or 'rejected'")
    req = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Leave request not found")
    req.status = data.status
    req.approved_by = current_user.id
    # Update leave balance when approved
    if data.status == "approved":
        bal = db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.year == req.start_date.year,
            LeaveBalance.leave_type == req.leave_type,
        ).first()
        if bal:
            bal.taken_days += req.days
    db.commit()
    db.refresh(req)
    return req


# ── Attendance ───────────────────────────────────────────────────────────────

@router.post("/attendance", response_model=AttendanceOut)
def record_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_employee_or_404(db, data.employee_id)
    # Upsert — one record per employee per day
    existing = db.query(Attendance).filter(
        Attendance.employee_id == data.employee_id,
        Attendance.date == data.date,
    ).first()
    if existing:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    att = Attendance(**data.model_dump())
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


@router.get("/attendance", response_model=list[AttendanceOut])
def list_attendance(
    employee_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Attendance)
    # Non-management users can only see their own attendance
    if current_user.role.name not in _WRITE_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id is None:
            return []
        q = q.filter(Attendance.employee_id == own_id)
    elif employee_id:
        q = q.filter(Attendance.employee_id == employee_id)
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    return q.order_by(Attendance.date.desc()).all()


# ── Leave Balances ───────────────────────────────────────────────────────────

@router.get("/leave-balances/{employee_id}", response_model=list[LeaveBalanceOut])
def get_leave_balances(
    employee_id: int,
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_employee_or_404(db, employee_id)
    # Non-management users can only view their own leave balances
    if current_user.role.name not in _WRITE_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id != employee_id:
            raise HTTPException(403, "Not authorised to view this employee's leave balances")
    if year is None:
        year = date.today().year
    balances = db.query(LeaveBalance).filter(
        LeaveBalance.employee_id == employee_id,
        LeaveBalance.year == year,
    ).all()
    result = []
    for b in balances:
        out = LeaveBalanceOut.model_validate(b)
        out.remaining_days = max(0.0, b.entitled_days - b.taken_days)
        result.append(out)
    return result


# ── Payroll ──────────────────────────────────────────────────────────────────

@router.post("/payroll/run", response_model=PayrollRunOut)
def run_payroll(
    data: PayrollRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _PAYROLL_ROLES:
        raise HTTPException(403, "Insufficient permissions")
    emp = _get_employee_or_404(db, data.employee_id)

    # Duplicate guard
    existing = db.query(PayrollRun).filter(
        PayrollRun.employee_id == data.employee_id,
        PayrollRun.month == data.month,
        PayrollRun.year == data.year,
    ).first()
    if existing:
        raise HTTPException(409, f"Payroll already exists for {data.month}/{data.year}")

    # Attendance summary for the month
    att_rows = db.query(Attendance).filter(
        Attendance.employee_id == data.employee_id,
        extract("month", Attendance.date) == data.month,
        extract("year", Attendance.date) == data.year,
    ).all()

    present_days = sum(
        1.0 for a in att_rows if a.status == "present"
    ) + sum(0.5 for a in att_rows if a.status == "half_day")
    leave_days = sum(1.0 for a in att_rows if a.status == "leave")
    total_ot_hours = sum(a.overtime_hours for a in att_rows)

    working_days = WORKING_DAYS_PER_MONTH
    paid_days = present_days + leave_days
    absent_days = max(0.0, working_days - paid_days)

    # Earnings
    daily_rate = emp.base_salary / working_days
    basic_salary = round(daily_rate * paid_days, 2)
    hra_prorated = round((emp.hra / working_days) * paid_days, 2)

    # OT pay: hourly rate = (basic / working_days / 8) × 2
    hourly_rate = emp.base_salary / working_days / 8
    ot_pay = round(total_ot_hours * hourly_rate * HOURLY_OT_MULTIPLIER, 2)

    gross_salary = round(basic_salary + hra_prorated + data.other_allowances + ot_pay, 2)

    # Deductions
    pf_employee = round(basic_salary * 0.12, 2)
    pf_employer = round(basic_salary * 0.12, 2)
    esi_employee = round(gross_salary * 0.0075, 2)
    esi_employer = round(gross_salary * 0.0325, 2)
    total_deductions = round(pf_employee + esi_employee + data.tds + data.other_deductions, 2)
    net_pay = round(gross_salary - total_deductions, 2)

    run = PayrollRun(
        employee_id=data.employee_id,
        month=data.month,
        year=data.year,
        basic_salary=basic_salary,
        hra=hra_prorated,
        other_allowances=data.other_allowances,
        overtime_hours=total_ot_hours,
        ot_pay=ot_pay,
        gross_salary=gross_salary,
        pf_employee=pf_employee,
        pf_employer=pf_employer,
        esi_employee=esi_employee,
        esi_employer=esi_employer,
        tds=data.tds,
        other_deductions=data.other_deductions,
        total_deductions=total_deductions,
        net_pay=net_pay,
        working_days=working_days,
        present_days=present_days,
        absent_days=absent_days,
        leave_days=leave_days,
        status="draft",
        processed_by=current_user.id,
        notes=data.notes,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.get("/payroll", response_model=list[PayrollRunOut])
def list_payroll(
    employee_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PayrollRun)
    # Non-payroll-role users can only see their own payslips
    if current_user.role.name not in _PAYROLL_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id is None:
            return []
        q = q.filter(PayrollRun.employee_id == own_id)
    elif employee_id:
        q = q.filter(PayrollRun.employee_id == employee_id)
    if month:
        q = q.filter(PayrollRun.month == month)
    if year:
        q = q.filter(PayrollRun.year == year)
    if status:
        q = q.filter(PayrollRun.status == status)
    return q.order_by(PayrollRun.year.desc(), PayrollRun.month.desc()).all()


@router.get("/payroll/{employee_id}/{year}/{month}", response_model=PayrollRunOut)
def get_payslip(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Non-payroll-role users can only access their own payslip
    if current_user.role.name not in _PAYROLL_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id != employee_id:
            raise HTTPException(403, "Not authorised to view this payslip")
    run = db.query(PayrollRun).filter(
        PayrollRun.employee_id == employee_id,
        PayrollRun.year == year,
        PayrollRun.month == month,
    ).first()
    if not run:
        raise HTTPException(404, "Payroll record not found")
    return run


@router.put("/payroll/{payroll_id}/status")
def update_payroll_status(
    payroll_id: int,
    status: str = Query(..., description="processed | paid"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _PAYROLL_ROLES:
        raise HTTPException(403, "Insufficient permissions")
    if status not in ("processed", "paid"):
        raise HTTPException(400, "status must be 'processed' or 'paid'")
    run = db.query(PayrollRun).filter(PayrollRun.id == payroll_id).first()
    if not run:
        raise HTTPException(404, "Payroll record not found")
    run.status = status
    db.commit()
    return {"id": payroll_id, "status": status}


# ── Performance Reviews ──────────────────────────────────────────────────────

@router.post("/performance-reviews", response_model=PerformanceReviewOut)
def create_performance_review(
    data: PerformanceReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    _get_employee_or_404(db, data.employee_id)
    overall = round(
        (data.productivity_score + data.quality_score +
         data.punctuality_score + data.teamwork_score) / 4,
        2,
    )
    review = PerformanceReview(
        **data.model_dump(),
        overall_score=overall,
        status="draft",
        reviewed_by=current_user.id,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/performance-reviews", response_model=list[PerformanceReviewOut])
def list_performance_reviews(
    employee_id: Optional[int] = None,
    review_period: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PerformanceReview)
    # Non-management users can only see their own performance reviews
    if current_user.role.name not in _WRITE_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id is None:
            return []
        q = q.filter(PerformanceReview.employee_id == own_id)
    elif employee_id:
        q = q.filter(PerformanceReview.employee_id == employee_id)
    if review_period:
        q = q.filter(PerformanceReview.review_period == review_period)
    return q.order_by(PerformanceReview.review_date.desc()).all()


@router.put("/performance-reviews/{review_id}/finalize", response_model=PerformanceReviewOut)
def finalize_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    review = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    review.status = "final"
    db.commit()
    db.refresh(review)
    return review


# ── Training Records ─────────────────────────────────────────────────────────

@router.post("/training", response_model=TrainingRecordOut)
def create_training_record(
    data: TrainingRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    _get_employee_or_404(db, data.employee_id)
    record = TrainingRecord(**data.model_dump(), status="scheduled")
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/training/{employee_id}", response_model=list[TrainingRecordOut])
def get_training_history(
    employee_id: int,
    training_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_employee_or_404(db, employee_id)
    # Non-management users can only see their own training history
    if current_user.role.name not in _WRITE_ROLES:
        own_id = _own_employee_id(db, current_user)
        if own_id != employee_id:
            raise HTTPException(403, "Not authorised to view this employee's training records")
    q = db.query(TrainingRecord).filter(TrainingRecord.employee_id == employee_id)
    if training_type:
        q = q.filter(TrainingRecord.training_type == training_type)
    if status:
        q = q.filter(TrainingRecord.status == status)
    return q.order_by(TrainingRecord.start_date.desc()).all()


@router.put("/training/{record_id}/complete", response_model=TrainingRecordOut)
def complete_training(
    record_id: int,
    score: Optional[float] = Query(default=None),
    certificate_url: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    record = db.query(TrainingRecord).filter(TrainingRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "Training record not found")
    record.status = "completed"
    if score is not None:
        record.score = score
    if certificate_url is not None:
        record.certificate_url = certificate_url
    db.commit()
    db.refresh(record)
    return record
