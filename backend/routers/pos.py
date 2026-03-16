"""Point-of-Sale router — sessions, checkout, transactions, barcode lookup."""
from datetime import datetime, timezone, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models.store import ProductCatalog
from backend.models.supply_chain import StoreStock
from backend.models.retail import POSSession, POSTransaction, POSTransactionItem
from backend.models.financial import Invoice, InvoiceItem
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.services.activity_log_service import log_activity
from backend.services.barcode_service import resolve_barcode
from backend.schemas import (
    POSSessionCreate, POSSessionOut, POSSessionClose,
    POSCheckoutIn, POSTransactionOut, POSTransactionItemOut,
    BarcodeScanResult,
)

router = APIRouter(prefix="/api/store/pos", tags=["Store — POS"])

CASHIER_ROLES = ("admin", "manager", "store_manager", "cashier")
ADMIN_ROLES = ("admin", "store_manager")


def _session_code(db: Session) -> str:
    count = db.query(POSSession).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"SES-{ts}-{count + 1:04d}"


def _txn_code(db: Session) -> str:
    count = db.query(POSTransaction).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"TXN-{ts}-{count + 1:04d}"


def _invoice_number(db: Session) -> str:
    count = db.query(Invoice).count()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"INV-POS-{ts}-{count + 1:04d}"


# ═══════════════════════════════════════════════════════════════
# POS SESSIONS
# ═══════════════════════════════════════════════════════════════

@router.post("/sessions", response_model=POSSessionOut, status_code=201)
def open_session(
    data: POSSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in CASHIER_ROLES:
        raise HTTPException(403, "Cashier or store_manager role required")
    # Only one open session per cashier
    existing = (
        db.query(POSSession)
        .filter(POSSession.cashier_id == current_user.id, POSSession.status == "open")
        .first()
    )
    if existing:
        raise HTTPException(400, "You already have an open POS session")

    session = POSSession(
        session_code=_session_code(db),
        cashier_id=current_user.id,
        opened_at=datetime.now(timezone.utc),
        opening_cash=data.opening_cash,
        notes=data.notes,
        status="open",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/active", response_model=POSSessionOut)
def get_active_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the caller's current open POS session."""
    session = (
        db.query(POSSession)
        .filter(POSSession.cashier_id == current_user.id, POSSession.status == "open")
        .first()
    )
    if not session:
        raise HTTPException(404, "No active POS session")
    return session


@router.get("/sessions", response_model=List[POSSessionOut])
def list_sessions(
    status: Optional[str] = Query(None),
    cashier_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required")
    q = db.query(POSSession)
    if status:
        q = q.filter(POSSession.status == status)
    if cashier_id:
        q = q.filter(POSSession.cashier_id == cashier_id)
    return q.order_by(POSSession.opened_at.desc()).limit(limit).all()


@router.put("/sessions/{session_id}/close", response_model=POSSessionOut)
def close_session(
    session_id: int,
    data: POSSessionClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(POSSession).filter(POSSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.cashier_id != current_user.id and current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Not authorised to close this session")
    if session.status != "open":
        raise HTTPException(400, f"Session is already '{session.status}'")

    session.status = "closed"
    session.closed_at = datetime.now(timezone.utc)
    session.closing_cash = data.closing_cash
    if data.notes:
        session.notes = data.notes
    db.commit()
    db.refresh(session)
    return session


# ═══════════════════════════════════════════════════════════════
# CHECKOUT
# ═══════════════════════════════════════════════════════════════

@router.post("/checkout", response_model=POSTransactionOut, status_code=201)
def checkout(
    data: POSCheckoutIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in CASHIER_ROLES:
        raise HTTPException(403, "Cashier role required")
    if not data.items:
        raise HTTPException(400, "Cart is empty")

    # Validate session
    session = db.query(POSSession).filter(POSSession.id == data.session_id).first()
    if not session:
        raise HTTPException(404, "POS session not found")
    if session.status != "open":
        raise HTTPException(400, "POS session is not open")
    if session.cashier_id != current_user.id and current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Session belongs to another cashier")

    now = datetime.now(timezone.utc)
    subtotal = 0.0
    discount_total = 0.0
    tax_total = 0.0
    txn_items: List[POSTransactionItem] = []

    # Pre-validate all items and lock stock
    stock_deductions: dict[int, float] = {}
    for item_in in data.items:
        product = db.query(ProductCatalog).filter(ProductCatalog.id == item_in.product_id).first()
        if not product or not product.is_active:
            raise HTTPException(404, f"Product id={item_in.product_id} not found or inactive")

        stock = db.query(StoreStock).filter(StoreStock.product_id == item_in.product_id).first()
        if not stock:
            raise HTTPException(400, f"No stock record for product '{product.name}'")
        needed = stock_deductions.get(item_in.product_id, 0) + item_in.quantity
        if stock.available_qty < needed:
            raise HTTPException(
                400,
                f"Insufficient stock for '{product.name}'. Available: {stock.available_qty} {product.unit}",
            )
        stock_deductions[item_in.product_id] = needed

    # Build transaction items and compute totals
    for item_in in data.items:
        product = db.query(ProductCatalog).filter(ProductCatalog.id == item_in.product_id).first()
        unit_price = item_in.unit_price if item_in.unit_price is not None else product.selling_price
        line_gross = unit_price * item_in.quantity
        line_discount = round(line_gross * item_in.discount_pct / 100, 4)
        line_after_disc = line_gross - line_discount
        line_tax = round(line_after_disc * product.gst_rate / 100, 4)
        line_total = round(line_after_disc + line_tax, 2)

        subtotal += round(line_gross, 4)
        discount_total += line_discount
        tax_total += line_tax

        txn_items.append(
            POSTransactionItem(
                product_id=product.id,
                product_name=product.name,
                barcode=product.barcode,
                quantity=item_in.quantity,
                unit=product.unit,
                unit_price=unit_price,
                discount_pct=item_in.discount_pct,
                tax_rate=product.gst_rate,
                total=line_total,
            )
        )

    total_amount = round(subtotal - discount_total + tax_total, 2)
    change_given = max(0.0, round(data.amount_tendered - total_amount, 2))

    # Create the POS transaction
    txn = POSTransaction(
        transaction_code=_txn_code(db),
        session_id=session.id,
        customer_id=data.customer_id,
        cashier_id=current_user.id,
        transaction_time=now,
        subtotal=round(subtotal, 2),
        discount_amount=round(discount_total, 2),
        tax_amount=round(tax_total, 2),
        total_amount=total_amount,
        amount_tendered=data.amount_tendered,
        change_given=change_given,
        payment_mode=data.payment_mode,
        payment_reference=data.payment_reference,
        status="completed",
        notes=data.notes,
    )
    db.add(txn)
    db.flush()  # get txn.id

    for item in txn_items:
        item.transaction_id = txn.id
        db.add(item)

    # Deduct stock
    for product_id, qty in stock_deductions.items():
        stock = db.query(StoreStock).filter(StoreStock.product_id == product_id).first()
        stock.current_qty = round(stock.current_qty - qty, 4)
        stock.updated_at = now

    # Create Invoice record
    invoice_date_val = date.today()
    invoice = Invoice(
        invoice_number=_invoice_number(db),
        invoice_type="sales",
        customer_id=data.customer_id,
        invoice_date=invoice_date_val,
        due_date=invoice_date_val,
        subtotal=txn.subtotal,
        cgst=round(tax_total / 2, 2),
        sgst=round(tax_total / 2, 2),
        igst=0,
        total_amount=total_amount,
        amount_paid=total_amount,
        balance_due=0,
        status="paid",
        notes=f"POS Transaction {txn.transaction_code}",
    )
    db.add(invoice)
    db.flush()
    txn.invoice_id = invoice.id

    # Update session totals
    session.total_sales = round(session.total_sales + total_amount, 2)
    session.total_transactions = session.total_transactions + 1

    # Audit log
    log_activity(
        db=db,
        action="CHECKOUT",
        module="store",
        username=current_user.username,
        user_id=current_user.id,
        entity_type="POSTransaction",
        entity_id=txn.id,
        description=f"POS sale {txn.transaction_code} total={total_amount}",
        ip=request.client.host if request.client else None,
    )

    db.commit()
    # Re-query with joinedload to guarantee items are included in the response
    txn = (
        db.query(POSTransaction)
        .options(joinedload(POSTransaction.items))
        .filter(POSTransaction.id == txn.id)
        .first()
    )
    return txn


# ═══════════════════════════════════════════════════════════════
# TRANSACTIONS
# ═══════════════════════════════════════════════════════════════

@router.get("/transactions", response_model=List[POSTransactionOut])
def list_transactions(
    session_id: Optional[int] = Query(None),
    cashier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    payment_mode: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(POSTransaction).options(joinedload(POSTransaction.items))
    if session_id:
        q = q.filter(POSTransaction.session_id == session_id)
    if cashier_id:
        q = q.filter(POSTransaction.cashier_id == cashier_id)
    if status:
        q = q.filter(POSTransaction.status == status)
    if payment_mode:
        q = q.filter(POSTransaction.payment_mode == payment_mode)
    if start_date:
        q = q.filter(POSTransaction.transaction_time >= start_date)
    if end_date:
        q = q.filter(POSTransaction.transaction_time <= end_date)
    return q.order_by(POSTransaction.transaction_time.desc()).limit(limit).all()


@router.get("/transactions/{txn_id}", response_model=POSTransactionOut)
def get_transaction(
    txn_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txn = (
        db.query(POSTransaction)
        .options(joinedload(POSTransaction.items))
        .filter(POSTransaction.id == txn_id)
        .first()
    )
    if not txn:
        raise HTTPException(404, "Transaction not found")
    return txn


@router.post("/transactions/{txn_id}/void")
def void_transaction(
    txn_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or store_manager role required to void transactions")

    txn = (
        db.query(POSTransaction)
        .options(joinedload(POSTransaction.items))
        .filter(POSTransaction.id == txn_id)
        .first()
    )
    if not txn:
        raise HTTPException(404, "Transaction not found")
    if txn.status != "completed":
        raise HTTPException(400, f"Transaction is '{txn.status}', cannot void")

    now = datetime.now(timezone.utc)

    # Restore stock
    for item in txn.items:
        stock = db.query(StoreStock).filter(StoreStock.product_id == item.product_id).first()
        if stock:
            stock.current_qty = round(stock.current_qty + item.quantity, 4)
            stock.updated_at = now

    txn.status = "voided"

    # Update session totals
    session = db.query(POSSession).filter(POSSession.id == txn.session_id).first()
    if session:
        session.total_sales = max(0.0, round(session.total_sales - txn.total_amount, 2))
        session.total_transactions = max(0, session.total_transactions - 1)

    log_activity(
        db=db,
        action="VOID_TRANSACTION",
        module="store",
        username=current_user.username,
        user_id=current_user.id,
        entity_type="POSTransaction",
        entity_id=txn.id,
        description=f"Voided transaction {txn.transaction_code}",
        ip=request.client.host if request.client else None,
    )

    db.commit()
    return {"message": f"Transaction {txn.transaction_code} voided", "transaction_id": txn_id}


# ═══════════════════════════════════════════════════════════════
# BARCODE LOOKUP
# ═══════════════════════════════════════════════════════════════

@router.get("/lookup/{barcode}", response_model=BarcodeScanResult)
def lookup_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = resolve_barcode(db, barcode)
    if result:
        db.commit()  # persist scan_count update if any
        return BarcodeScanResult(barcode=barcode, found=True, result=result)
    return BarcodeScanResult(barcode=barcode, found=False, message="Barcode not found")
