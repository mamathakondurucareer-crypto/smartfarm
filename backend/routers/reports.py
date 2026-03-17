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
from backend.models.inventory import InventoryItem, InventoryTransaction
from backend.models.user import User, Employee, Attendance
from backend.models.aquaculture import FeedLog as AquaFeedLog, FishBatch, Pond
from backend.models.poultry import PoultryFeedLog, PoultryFlock
from backend.models.qa_traceability import ProductLot, QualityTest
from backend.models.sensor import SensorDevice, Alert
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


# ═══════════════════════════════════════════════════════════════
# DAILY FARM REPORT
# ═══════════════════════════════════════════════════════════════

@router.get("/daily-farm")
def daily_farm_report(
    report_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Consolidated daily snapshot: sales, attendance, alerts, inventory movements."""
    _require_report_role(current_user)
    target = report_date or date.today()
    day_start = datetime(target.year, target.month, target.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = datetime(target.year, target.month, target.day, 23, 59, 59, tzinfo=timezone.utc)

    # Sales
    txns = db.query(POSTransaction).filter(
        POSTransaction.status == "completed",
        POSTransaction.transaction_time >= day_start,
        POSTransaction.transaction_time <= day_end,
    ).all()
    daily_sales = round(sum(t.total_amount for t in txns), 2)

    # Revenue entries
    rev_entries = db.query(RevenueEntry).filter(RevenueEntry.entry_date == target).all()
    daily_revenue = round(sum(r.total_amount for r in rev_entries), 2)

    # Expense entries
    exp_entries = db.query(ExpenseEntry).filter(ExpenseEntry.entry_date == target).all()
    daily_expenses = round(sum(e.total_amount for e in exp_entries), 2)

    # Attendance
    try:
        attendance_count = db.query(Attendance).filter(Attendance.date == target).count()
        present_count = db.query(Attendance).filter(
            Attendance.date == target, Attendance.status == "present"
        ).count()
    except Exception:
        attendance_count = present_count = 0

    # Active alerts
    try:
        active_alerts = db.query(Alert).filter(Alert.resolved == False).count()
        critical_alerts = db.query(Alert).filter(
            Alert.resolved == False, Alert.alert_type == "critical"
        ).count()
    except Exception:
        active_alerts = critical_alerts = 0

    # Production batches today
    prod_batches = db.query(ProductionBatch).filter(
        ProductionBatch.production_date == target
    ).all()

    return {
        "report_date": target.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sales": {
            "pos_transactions": len(txns),
            "pos_revenue": daily_sales,
        },
        "financial": {
            "revenue_entries": len(rev_entries),
            "total_revenue": daily_revenue,
            "expense_entries": len(exp_entries),
            "total_expenses": daily_expenses,
            "net": round(daily_revenue - daily_expenses, 2),
        },
        "workforce": {
            "total_records": attendance_count,
            "present": present_count,
        },
        "operations": {
            "production_batches": len(prod_batches),
            "production_summary": {b.category: round(b.final_quantity, 2) for b in prod_batches},
        },
        "alerts": {
            "active": active_alerts,
            "critical": critical_alerts,
        },
    }


# ═══════════════════════════════════════════════════════════════
# WEEKLY SUMMARY
# ═══════════════════════════════════════════════════════════════

@router.get("/weekly-summary")
def weekly_summary(
    week_start: Optional[date] = Query(None, description="Monday of the week (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """7-day aggregated summary from week_start (defaults to current week Monday)."""
    _require_report_role(current_user)

    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    rev_q = db.query(RevenueEntry).filter(
        RevenueEntry.entry_date >= week_start,
        RevenueEntry.entry_date <= week_end,
    ).all()
    exp_q = db.query(ExpenseEntry).filter(
        ExpenseEntry.entry_date >= week_start,
        ExpenseEntry.entry_date <= week_end,
    ).all()

    total_rev = round(sum(r.total_amount for r in rev_q), 2)
    total_exp = round(sum(e.total_amount for e in exp_q), 2)

    # Daily breakdown
    daily: dict = {}
    for r in rev_q:
        k = r.entry_date.isoformat()
        daily.setdefault(k, {"revenue": 0.0, "expenses": 0.0})
        daily[k]["revenue"] = round(daily[k]["revenue"] + r.total_amount, 2)
    for e in exp_q:
        k = e.entry_date.isoformat()
        daily.setdefault(k, {"revenue": 0.0, "expenses": 0.0})
        daily[k]["expenses"] = round(daily[k]["expenses"] + e.total_amount, 2)

    prod_batches = db.query(ProductionBatch).filter(
        ProductionBatch.production_date >= week_start,
        ProductionBatch.production_date <= week_end,
    ).all()
    prod_by_category: dict = {}
    for b in prod_batches:
        prod_by_category[b.category] = round(prod_by_category.get(b.category, 0) + b.final_quantity, 2)

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "total_revenue": total_rev,
        "total_expenses": total_exp,
        "net_profit": round(total_rev - total_exp, 2),
        "daily_breakdown": {k: v for k, v in sorted(daily.items())},
        "production_by_category": prod_by_category,
    }


# ═══════════════════════════════════════════════════════════════
# MONTHLY P&L
# ═══════════════════════════════════════════════════════════════

@router.get("/monthly-pl")
def monthly_pl(
    year: int = Query(default=2025),
    month: int = Query(default=1, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full month P&L: revenue by stream, expenses by category, gross/net margin."""
    _require_report_role(current_user)

    import calendar
    _, last_day = calendar.monthrange(year, month)
    m_start = date(year, month, 1)
    m_end = date(year, month, last_day)

    revenues = db.query(RevenueEntry).filter(
        RevenueEntry.entry_date >= m_start, RevenueEntry.entry_date <= m_end
    ).all()
    expenses = db.query(ExpenseEntry).filter(
        ExpenseEntry.entry_date >= m_start, ExpenseEntry.entry_date <= m_end
    ).all()

    total_rev = round(sum(r.total_amount for r in revenues), 2)
    total_exp = round(sum(e.total_amount for e in expenses), 2)
    gross = round(total_rev - total_exp, 2)
    margin = round(gross / total_rev * 100, 2) if total_rev else 0.0

    by_stream: dict = {}
    for r in revenues:
        by_stream[r.stream] = round(by_stream.get(r.stream, 0) + r.total_amount, 2)

    by_category: dict = {}
    for e in expenses:
        by_category[e.category] = round(by_category.get(e.category, 0) + e.total_amount, 2)

    # POS contribution
    pos_start = datetime(year, month, 1, tzinfo=timezone.utc)
    pos_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    pos_txns = db.query(POSTransaction).filter(
        POSTransaction.status == "completed",
        POSTransaction.transaction_time >= pos_start,
        POSTransaction.transaction_time <= pos_end,
    ).all()
    pos_revenue = round(sum(t.total_amount for t in pos_txns), 2)

    return {
        "year": year,
        "month": month,
        "period": f"{m_start.isoformat()} to {m_end.isoformat()}",
        "revenue": {
            "total": total_rev,
            "by_stream": by_stream,
            "pos_sales": pos_revenue,
        },
        "expenses": {
            "total": total_exp,
            "by_category": by_category,
        },
        "profitability": {
            "gross_profit": gross,
            "gross_margin_pct": margin,
        },
    }


# ═══════════════════════════════════════════════════════════════
# INVESTOR QUARTERLY REPORT
# ═══════════════════════════════════════════════════════════════

@router.get("/investor-quarterly")
def investor_quarterly(
    year: int = Query(default=2025),
    quarter: int = Query(default=1, ge=1, le=4),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Investor-facing quarterly summary: revenue, production volume, key KPIs."""
    _require_report_role(current_user)

    import calendar
    q_month_start = (quarter - 1) * 3 + 1
    q_month_end = q_month_start + 2
    _, last_day = calendar.monthrange(year, q_month_end)
    q_start = date(year, q_month_start, 1)
    q_end = date(year, q_month_end, last_day)

    revenues = db.query(RevenueEntry).filter(
        RevenueEntry.entry_date >= q_start, RevenueEntry.entry_date <= q_end
    ).all()
    expenses = db.query(ExpenseEntry).filter(
        ExpenseEntry.entry_date >= q_start, ExpenseEntry.entry_date <= q_end
    ).all()

    total_rev = round(sum(r.total_amount for r in revenues), 2)
    total_exp = round(sum(e.total_amount for e in expenses), 2)
    net_profit = round(total_rev - total_exp, 2)

    prod_batches = db.query(ProductionBatch).filter(
        ProductionBatch.production_date >= q_start,
        ProductionBatch.production_date <= q_end,
    ).all()
    total_production_kg = round(sum(b.final_quantity for b in prod_batches), 2)

    by_stream: dict = {}
    for r in revenues:
        by_stream[r.stream] = round(by_stream.get(r.stream, 0) + r.total_amount, 2)

    return {
        "year": year,
        "quarter": f"Q{quarter}",
        "period": f"{q_start.isoformat()} to {q_end.isoformat()}",
        "financial_summary": {
            "total_revenue": total_rev,
            "total_expenses": total_exp,
            "net_profit": net_profit,
            "profit_margin_pct": round(net_profit / total_rev * 100, 2) if total_rev else 0.0,
            "revenue_by_stream": by_stream,
        },
        "operations": {
            "production_batches": len(prod_batches),
            "total_production_kg": total_production_kg,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
# FEED COST ANALYSIS BY SPECIES
# ═══════════════════════════════════════════════════════════════

@router.get("/feed-cost-analysis")
def feed_cost_analysis(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Feed cost breakdown by species (aquaculture + poultry)."""
    _require_report_role(current_user)

    result: dict = {}

    # Aquaculture feed
    try:
        aq_q = db.query(AquaFeedLog)
        if start_date:
            aq_q = aq_q.filter(AquaFeedLog.feed_date >= start_date)
        if end_date:
            aq_q = aq_q.filter(AquaFeedLog.feed_date <= end_date)
        aq_logs = aq_q.all()

        for log in aq_logs:
            species = "fish"
            if species not in result:
                result[species] = {"total_feed_kg": 0.0, "total_cost": 0.0, "entries": 0}
            result[species]["total_feed_kg"] = round(result[species]["total_feed_kg"] + (log.quantity_kg or 0), 2)
            result[species]["total_cost"] = round(result[species]["total_cost"] + (log.cost or 0), 2)
            result[species]["entries"] += 1
    except Exception:
        pass

    # Poultry feed
    try:
        po_q = db.query(PoultryFeedLog)
        if start_date:
            po_q = po_q.filter(PoultryFeedLog.feed_date >= start_date)
        if end_date:
            po_q = po_q.filter(PoultryFeedLog.feed_date <= end_date)
        po_logs = po_q.all()

        for log in po_logs:
            species = getattr(log, "species", "poultry") or "poultry"
            if species not in result:
                result[species] = {"total_feed_kg": 0.0, "total_cost": 0.0, "entries": 0}
            result[species]["total_feed_kg"] = round(result[species]["total_feed_kg"] + (log.quantity_kg or 0), 2)
            result[species]["total_cost"] = round(result[species]["total_cost"] + (log.cost or 0), 2)
            result[species]["entries"] += 1
    except Exception:
        pass

    total_cost = round(sum(v["total_cost"] for v in result.values()), 2)

    for species_data in result.values():
        kg = species_data["total_feed_kg"]
        cost = species_data["total_cost"]
        species_data["cost_per_kg"] = round(cost / kg, 2) if kg else 0.0

    return {
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
        },
        "total_feed_cost": total_cost,
        "by_species": result,
    }


# ═══════════════════════════════════════════════════════════════
# LOT TRACEABILITY REPORT
# ═══════════════════════════════════════════════════════════════

@router.get("/lot-traceability/{batch_id}")
def lot_traceability(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full traceability chain for a product lot: QA tests, production batch, source."""
    _require_report_role(current_user)

    lot = db.query(ProductLot).filter(ProductLot.lot_number == batch_id).first()
    if not lot:
        raise HTTPException(404, f"Product lot '{batch_id}' not found")

    qa_tests = db.query(QualityTest).filter(QualityTest.lot_id == lot.id).all()

    production = None
    if lot.production_batch_id:
        production = db.query(ProductionBatch).filter(
            ProductionBatch.id == lot.production_batch_id
        ).first()

    return {
        "lot_number": lot.lot_number,
        "product_name": lot.product_name,
        "category": lot.category,
        "quantity_kg": lot.quantity_kg,
        "unit": lot.unit,
        "production_date": lot.production_date.isoformat() if lot.production_date else None,
        "expiry_date": lot.expiry_date.isoformat() if lot.expiry_date else None,
        "status": lot.status,
        "source_batch": lot.source_batch_ref,
        "production_batch": {
            "id": production.id,
            "category": production.category,
            "source": production.source,
            "production_date": production.production_date.isoformat(),
            "final_quantity": production.final_quantity,
        } if production else None,
        "qa_tests": [
            {
                "id": t.id,
                "test_type": t.test_type,
                "test_date": t.test_date.isoformat(),
                "result": t.result,
                "passed": t.passed,
                "tested_by": t.tested_by,
            }
            for t in qa_tests
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
