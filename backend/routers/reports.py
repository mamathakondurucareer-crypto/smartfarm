"""Reports router — sales, production, financial summary, store daily, stock movement, inventory valuation."""
from datetime import datetime, timezone, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.retail import POSTransaction, POSTransactionItem
from backend.models.supply_chain import StoreStock, FarmSupplyTransfer
from backend.models.store import ProductCatalog, StoreConfig
from backend.models.financial import RevenueEntry, ExpenseEntry
from backend.models.production import ProductionBatch
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])

REPORT_ROLES = ("admin", "manager", "store_manager", "supervisor", "viewer")


def _require_report_role(current_user: User) -> None:
    if current_user.role.name not in REPORT_ROLES:
        raise HTTPException(403, "Insufficient permissions to view reports")


# ═══════════════════════════════════════════════════════════════
# SALES SUMMARY
# ═══════════════════════════════════════════════════════════════

@router.get("/sales")
def sales_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_role(current_user)

    q = db.query(POSTransaction).filter(POSTransaction.status == "completed")
    if start_date:
        q = q.filter(POSTransaction.transaction_time >= start_date)
    if end_date:
        q = q.filter(POSTransaction.transaction_time <= end_date)

    transactions = q.all()

    total_revenue = sum(t.total_amount for t in transactions)
    total_transactions = len(transactions)
    by_payment_mode: dict = {}
    for txn in transactions:
        by_payment_mode[txn.payment_mode] = by_payment_mode.get(txn.payment_mode, 0) + txn.total_amount

    # Top products by revenue from transaction items
    item_q = (
        db.query(
            POSTransactionItem.product_name,
            func.sum(POSTransactionItem.total).label("revenue"),
            func.sum(POSTransactionItem.quantity).label("qty_sold"),
        )
        .join(POSTransaction, POSTransactionItem.transaction_id == POSTransaction.id)
        .filter(POSTransaction.status == "completed")
    )
    if start_date:
        item_q = item_q.filter(POSTransaction.transaction_time >= start_date)
    if end_date:
        item_q = item_q.filter(POSTransaction.transaction_time <= end_date)
    top_products_raw = item_q.group_by(POSTransactionItem.product_name).order_by(func.sum(POSTransactionItem.total).desc()).limit(10).all()
    top_products = [
        {"product_name": row.product_name, "revenue": round(row.revenue, 2), "qty_sold": round(row.qty_sold, 2)}
        for row in top_products_raw
    ]

    # Sales by date
    by_date: dict = {}
    for txn in transactions:
        d = txn.transaction_time.date().isoformat() if txn.transaction_time else "unknown"
        by_date[d] = by_date.get(d, 0) + txn.total_amount

    return {
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
        },
        "total_revenue": round(total_revenue, 2),
        "total_transactions": total_transactions,
        "avg_transaction_value": round(total_revenue / total_transactions, 2) if total_transactions else 0,
        "by_payment_mode": {k: round(v, 2) for k, v in by_payment_mode.items()},
        "top_products": top_products,
        "by_date": {k: round(v, 2) for k, v in sorted(by_date.items())},
    }


# ═══════════════════════════════════════════════════════════════
# PRODUCTION REPORT
# ═══════════════════════════════════════════════════════════════

@router.get("/production")
def production_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_role(current_user)

    q = db.query(ProductionBatch)
    if start_date:
        q = q.filter(ProductionBatch.production_date >= start_date)
    if end_date:
        q = q.filter(ProductionBatch.production_date <= end_date)
    batches = q.all()

    total_batches = len(batches)
    by_category: dict = {}
    by_source: dict = {}
    total_value = 0.0

    for b in batches:
        by_category[b.category] = by_category.get(b.category, 0) + b.final_quantity
        by_source[b.source] = by_source.get(b.source, 0) + b.final_quantity
        total_value += b.total_cost if hasattr(b, "total_cost") and b.total_cost else 0

    return {
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
        },
        "total_batches": total_batches,
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "by_source": {k: round(v, 2) for k, v in by_source.items()},
        "total_value": round(total_value, 2),
    }


# ═══════════════════════════════════════════════════════════════
# FINANCIAL SUMMARY
# ═══════════════════════════════════════════════════════════════

@router.get("/financial-summary")
def financial_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_role(current_user)

    rev_q = db.query(RevenueEntry)
    exp_q = db.query(ExpenseEntry)
    if start_date:
        rev_q = rev_q.filter(RevenueEntry.entry_date >= start_date)
        exp_q = exp_q.filter(ExpenseEntry.entry_date >= start_date)
    if end_date:
        rev_q = rev_q.filter(RevenueEntry.entry_date <= end_date)
        exp_q = exp_q.filter(ExpenseEntry.entry_date <= end_date)

    revenues = rev_q.all()
    expenses = exp_q.all()

    total_revenue = sum(r.total_amount for r in revenues)
    total_expenses = sum(e.total_amount for e in expenses)
    gross_profit = total_revenue - total_expenses
    profit_margin = round((gross_profit / total_revenue * 100), 2) if total_revenue else 0

    revenue_by_stream: dict = {}
    for r in revenues:
        revenue_by_stream[r.stream] = revenue_by_stream.get(r.stream, 0) + r.total_amount

    expense_by_category: dict = {}
    for e in expenses:
        expense_by_category[e.category] = expense_by_category.get(e.category, 0) + e.total_amount

    # Monthly breakdown
    monthly: dict = {}
    for r in revenues:
        key = f"{r.entry_date.year}-{r.entry_date.month:02d}"
        if key not in monthly:
            monthly[key] = {"revenue": 0, "expenses": 0}
        monthly[key]["revenue"] += r.total_amount
    for e in expenses:
        key = f"{e.entry_date.year}-{e.entry_date.month:02d}"
        if key not in monthly:
            monthly[key] = {"revenue": 0, "expenses": 0}
        monthly[key]["expenses"] += e.total_amount

    monthly_data = [
        {
            "month": k,
            "revenue": round(v["revenue"], 2),
            "expenses": round(v["expenses"], 2),
            "profit": round(v["revenue"] - v["expenses"], 2),
        }
        for k, v in sorted(monthly.items())
    ]

    return {
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
        },
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "gross_profit": round(gross_profit, 2),
        "profit_margin_pct": profit_margin,
        "revenue_streams": {k: round(v, 2) for k, v in revenue_by_stream.items()},
        "expense_breakdown": {k: round(v, 2) for k, v in expense_by_category.items()},
        "monthly_data": monthly_data,
    }


# ═══════════════════════════════════════════════════════════════
# STORE DAILY SUMMARY
# ═══════════════════════════════════════════════════════════════

@router.get("/store-daily")
def store_daily_summary(
    report_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_role(current_user)

    target_date = report_date or date.today()
    day_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=timezone.utc)

    txns = (
        db.query(POSTransaction)
        .filter(
            POSTransaction.status == "completed",
            POSTransaction.transaction_time >= day_start,
            POSTransaction.transaction_time <= day_end,
        )
        .all()
    )

    total_sales = sum(t.total_amount for t in txns)
    cash_in_hand = sum(t.total_amount for t in txns if t.payment_mode == "cash")
    items_sold = 0

    product_totals: dict = {}
    for txn in txns:
        for item in txn.items:
            items_sold += item.quantity
            product_totals[item.product_name] = product_totals.get(item.product_name, 0) + item.total

    top_product = max(product_totals, key=product_totals.get) if product_totals else None

    return {
        "date": target_date.isoformat(),
        "total_transactions": len(txns),
        "total_sales": round(total_sales, 2),
        "cash_in_hand": round(cash_in_hand, 2),
        "items_sold": round(items_sold, 2),
        "top_product": top_product,
        "top_product_revenue": round(product_totals.get(top_product, 0), 2) if top_product else 0,
        "payment_breakdown": {
            mode: round(sum(t.total_amount for t in txns if t.payment_mode == mode), 2)
            for mode in set(t.payment_mode for t in txns)
        },
    }


# ═══════════════════════════════════════════════════════════════
# STOCK MOVEMENT SUMMARY
# ═══════════════════════════════════════════════════════════════

@router.get("/stock-movement")
def stock_movement_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_role(current_user)

    # IN: farm supply transfers received
    in_q = db.query(FarmSupplyTransfer).filter(FarmSupplyTransfer.status == "received")
    if start_date:
        in_q = in_q.filter(FarmSupplyTransfer.received_at >= start_date)
    if end_date:
        in_q = in_q.filter(FarmSupplyTransfer.received_at <= end_date)
    transfers_in = in_q.all()

    # OUT: completed POS transaction items
    out_q = (
        db.query(POSTransactionItem)
        .join(POSTransaction, POSTransactionItem.transaction_id == POSTransaction.id)
        .filter(POSTransaction.status == "completed")
    )
    if start_date:
        out_q = out_q.filter(POSTransaction.transaction_time >= start_date)
    if end_date:
        out_q = out_q.filter(POSTransaction.transaction_time <= end_date)
    sold_items = out_q.all()

    # Aggregate per product
    product_movements: dict = {}

    for t in transfers_in:
        name = t.product_name
        if name not in product_movements:
            product_movements[name] = {"in_qty": 0, "out_qty": 0, "in_value": 0, "out_value": 0}
        product_movements[name]["in_qty"] += t.quantity_transferred
        product_movements[name]["in_value"] += t.total_cost

    for item in sold_items:
        name = item.product_name
        if name not in product_movements:
            product_movements[name] = {"in_qty": 0, "out_qty": 0, "in_value": 0, "out_value": 0}
        product_movements[name]["out_qty"] += item.quantity
        product_movements[name]["out_value"] += item.total

    result = [
        {
            "product_name": name,
            "in_qty": round(v["in_qty"], 2),
            "out_qty": round(v["out_qty"], 2),
            "net_movement": round(v["in_qty"] - v["out_qty"], 2),
            "in_value": round(v["in_value"], 2),
            "out_value": round(v["out_value"], 2),
        }
        for name, v in sorted(product_movements.items())
    ]

    return {
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
        },
        "movements": result,
        "total_in_value": round(sum(r["in_value"] for r in result), 2),
        "total_out_value": round(sum(r["out_value"] for r in result), 2),
    }


# ═══════════════════════════════════════════════════════════════
# INVENTORY VALUATION
# ═══════════════════════════════════════════════════════════════

@router.get("/inventory-valuation")
def inventory_valuation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_role(current_user)

    stocks = db.query(StoreStock).all()
    items = []
    total_value = 0.0
    total_qty = 0.0

    for s in stocks:
        product = db.query(ProductCatalog).filter(ProductCatalog.id == s.product_id).first()
        value = s.total_value
        total_value += value
        total_qty += s.current_qty
        items.append({
            "product_id": s.product_id,
            "product_name": product.name if product else "Unknown",
            "product_code": product.product_code if product else None,
            "category": product.category if product else None,
            "current_qty": s.current_qty,
            "available_qty": s.available_qty,
            "unit": s.unit,
            "avg_cost_per_unit": s.avg_cost_per_unit,
            "total_value": value,
            "location": s.location,
        })

    items.sort(key=lambda x: x["total_value"], reverse=True)

    return {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "total_value": round(total_value, 2),
        "total_sku_count": len(items),
        "total_qty": round(total_qty, 2),
        "items": items,
    }
