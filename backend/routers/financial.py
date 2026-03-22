"""Financial management: revenue, expenses, salary, invoices, HR, attendance."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.financial import RevenueEntry, ExpenseEntry, SalaryRecord, Invoice, InvoiceItem, Budget
from backend.models.user import Employee, Attendance, LeaveRequest, User
from backend.routers.auth import get_current_user
from backend.schemas import (
    RevenueCreate, ExpenseCreate, SalaryRecordCreate, SalaryRecordOut,
    InvoiceCreate, EmployeeCreate, EmployeeOut, AttendanceCreate, LeaveRequestCreate,
)
from backend.utils.helpers import generate_code
from backend.services.activity_log_service import log_activity

router = APIRouter(prefix="/api/financial", tags=["Financial & HR"])

FINANCE_ROLES = ("admin", "manager", "accountant")
HR_ROLES = ("admin", "manager", "hr")


# ═══════ REVENUE ═══════
@router.post("/revenue", status_code=201)
def add_revenue(data: RevenueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    entry = RevenueEntry(**data.model_dump())
    db.add(entry)
    log_activity(db, "ADD_REVENUE", "financial", username=current_user.username,
                 user_id=current_user.id,
                 description=f"Revenue added: {data.stream} ₹{data.total_amount}")
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "total_amount": entry.total_amount}


@router.get("/revenue")
def list_revenue(
    stream: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "start_date must be before end_date")
    q = db.query(RevenueEntry)
    if stream:
        q = q.filter(RevenueEntry.stream == stream)
    if start_date:
        q = q.filter(RevenueEntry.entry_date >= start_date)
    if end_date:
        q = q.filter(RevenueEntry.entry_date <= end_date)
    return q.order_by(RevenueEntry.entry_date.desc()).limit(200).all()


# ═══════ EXPENSES ═══════
@router.post("/expenses", status_code=201)
def add_expense(data: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    entry = ExpenseEntry(**data.model_dump())
    db.add(entry)
    log_activity(db, "ADD_EXPENSE", "financial", username=current_user.username,
                 user_id=current_user.id,
                 description=f"Expense added: {data.category} ₹{data.total_amount}")
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "total_amount": entry.total_amount}


@router.get("/expenses")
def list_expenses(
    category: Optional[str] = None,
    department: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "start_date must be before end_date")
    q = db.query(ExpenseEntry)
    if category:
        q = q.filter(ExpenseEntry.category == category)
    if department:
        q = q.filter(ExpenseEntry.department == department)
    if start_date:
        q = q.filter(ExpenseEntry.entry_date >= start_date)
    if end_date:
        q = q.filter(ExpenseEntry.entry_date <= end_date)
    return q.order_by(ExpenseEntry.entry_date.desc()).limit(200).all()


# ═══════ P&L SUMMARY ═══════
@router.get("/pnl-summary")
def pnl_summary(start_date: date = Query(...), end_date: date = Query(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    if start_date > end_date:
        raise HTTPException(400, "start_date must be before end_date")
    revenue = db.query(func.coalesce(func.sum(RevenueEntry.total_amount), 0)).filter(
        RevenueEntry.entry_date.between(start_date, end_date)).scalar()
    expense = db.query(func.coalesce(func.sum(ExpenseEntry.total_amount), 0)).filter(
        ExpenseEntry.entry_date.between(start_date, end_date)).scalar()

    rev_by_stream = db.query(RevenueEntry.stream, func.sum(RevenueEntry.total_amount)).filter(
        RevenueEntry.entry_date.between(start_date, end_date)).group_by(RevenueEntry.stream).all()
    exp_by_cat = db.query(ExpenseEntry.category, func.sum(ExpenseEntry.total_amount)).filter(
        ExpenseEntry.entry_date.between(start_date, end_date)).group_by(ExpenseEntry.category).all()

    return {
        "period": {"start": str(start_date), "end": str(end_date)},
        "total_revenue": float(revenue),
        "total_expense": float(expense),
        "net_profit": float(revenue - expense),
        "margin_pct": round(float(revenue - expense) / float(revenue) * 100, 1) if revenue > 0 else 0,
        "revenue_breakdown": [{"stream": r[0], "amount": float(r[1])} for r in rev_by_stream],
        "expense_breakdown": [{"category": e[0], "amount": float(e[1])} for e in exp_by_cat],
    }


# ═══════ INVOICES ═══════
@router.post("/invoices", status_code=201)
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    count = db.query(func.count(Invoice.id)).scalar()
    prefix = "INV" if data.invoice_type == "sales" else "BILL"
    inv = Invoice(
        invoice_number=generate_code(prefix, count + 1),
        invoice_type=data.invoice_type,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        customer_id=data.customer_id,
        supplier_id=data.supplier_id,
        subtotal=0, total_amount=0, balance_due=0,
    )
    db.add(inv)
    db.flush()

    subtotal = 0
    gst_total = 0
    for item_data in data.items:
        total = item_data.quantity * item_data.unit_price
        gst = total * item_data.gst_rate / 100
        ii = InvoiceItem(
            invoice_id=inv.id, description=item_data.description,
            quantity=item_data.quantity, unit=item_data.unit,
            unit_price=item_data.unit_price, gst_rate=item_data.gst_rate,
            total=total + gst,
        )
        db.add(ii)
        subtotal += total
        gst_total += gst

    inv.subtotal = subtotal
    inv.cgst = gst_total / 2
    inv.sgst = gst_total / 2
    inv.total_amount = subtotal + gst_total
    inv.balance_due = inv.total_amount
    log_activity(db, "CREATE_INVOICE", "financial", username=current_user.username,
                 user_id=current_user.id, entity_type="Invoice",
                 description=f"Invoice created: {data.invoice_type} ₹{inv.total_amount:.2f}")
    db.commit()
    db.refresh(inv)
    return {"invoice_number": inv.invoice_number, "total_amount": inv.total_amount}


@router.get("/invoices")
def list_invoices(invoice_type: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in FINANCE_ROLES:
        raise HTTPException(403, "Finance role required")
    q = db.query(Invoice)
    if invoice_type:
        q = q.filter(Invoice.invoice_type == invoice_type)
    if status:
        q = q.filter(Invoice.status == status)
    return q.order_by(Invoice.invoice_date.desc()).limit(50).all()


# ═══════ EMPLOYEES / HR ═══════
@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(department: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    q = db.query(Employee).filter(Employee.is_active == True)
    if department:
        q = q.filter(Employee.department == department)
    return q.order_by(Employee.full_name).all()


@router.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/employees/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp


# ═══════ ATTENDANCE ═══════
@router.post("/attendance", status_code=201)
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    existing = db.query(Attendance).filter(
        Attendance.employee_id == data.employee_id, Attendance.date == data.date
    ).first()
    if existing:
        raise HTTPException(400, "Attendance already marked for this date")
    att = Attendance(**data.model_dump())
    db.add(att)
    db.commit()
    return {"id": att.id, "message": "Attendance marked"}


@router.get("/attendance")
def list_attendance(
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "start_date must be before end_date")
    q = db.query(Attendance)
    if employee_id:
        q = q.filter(Attendance.employee_id == employee_id)
    if start_date:
        q = q.filter(Attendance.date >= start_date)
    if end_date:
        q = q.filter(Attendance.date <= end_date)
    return q.order_by(Attendance.date.desc()).limit(500).all()


# ═══════ SALARY ═══════
@router.post("/salary/process", status_code=201)
def process_salary(data: SalaryRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")

    basic = emp.base_salary * (data.present_days / data.working_days) if data.working_days > 0 else 0
    hra = emp.hra * (data.present_days / data.working_days) if data.working_days > 0 else 0
    overtime_pay = data.overtime_hours * (emp.base_salary / (data.working_days * 8)) * 1.5 if data.working_days > 0 else 0
    gross = basic + hra + overtime_pay + data.bonus + data.allowances
    pf = gross * 0.12 if gross > 15000 else 0
    esi = gross * 0.0075 if gross <= 21000 else 0
    total_ded = pf + esi + data.other_deductions + data.advance_recovery
    net = gross - total_ded

    record = SalaryRecord(
        employee_id=data.employee_id, month=data.month, year=data.year,
        working_days=data.working_days, present_days=data.present_days,
        overtime_hours=data.overtime_hours,
        basic_salary=round(basic, 2), hra=round(hra, 2), overtime_pay=round(overtime_pay, 2),
        bonus=data.bonus, allowances=data.allowances,
        gross_salary=round(gross, 2),
        pf_deduction=round(pf, 2), esi_deduction=round(esi, 2),
        other_deductions=data.other_deductions, advance_recovery=data.advance_recovery,
        total_deductions=round(total_ded, 2),
        net_salary=round(net, 2),
        status="processed",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return SalaryRecordOut.model_validate(record)


@router.get("/salary")
def list_salary(
    employee_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    q = db.query(SalaryRecord)
    if employee_id:
        q = q.filter(SalaryRecord.employee_id == employee_id)
    if month:
        q = q.filter(SalaryRecord.month == month)
    if year:
        q = q.filter(SalaryRecord.year == year)
    return q.order_by(SalaryRecord.year.desc(), SalaryRecord.month.desc()).limit(100).all()


# ═══════ LEAVE ═══════
@router.post("/leave-requests", status_code=201)
def submit_leave(data: LeaveRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lr = LeaveRequest(**data.model_dump())
    db.add(lr)
    db.commit()
    return {"id": lr.id, "status": "pending"}


@router.put("/leave-requests/{lr_id}/approve")
def approve_leave(lr_id: int, approved_by: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in HR_ROLES:
        raise HTTPException(403, "HR role required")
    lr = db.query(LeaveRequest).filter(LeaveRequest.id == lr_id).first()
    if not lr:
        raise HTTPException(404, "Leave request not found")
    lr.status = "approved"
    lr.approved_by = approved_by
    db.commit()
    return {"message": "Leave approved"}
