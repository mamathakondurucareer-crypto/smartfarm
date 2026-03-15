"""Incident tracking and production management endpoints."""

from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.incident import Incident, IncidentAction, MaintenanceSchedule
from backend.models.production import ProductionBatch, ProcessingLog, PackagingLog, QualityCheck, StockLedger, StockMovement
from backend.schemas import (
    IncidentCreate, IncidentActionCreate, MaintenanceCreate,
    ProductionBatchCreate, ProcessingLogCreate, PackagingLogCreate,
    QualityCheckCreate, StockMovementCreate,
)
from backend.utils.helpers import generate_code

incidents_router = APIRouter(prefix="/api/incidents", tags=["Incidents & Maintenance"])
production_router = APIRouter(prefix="/api/production", tags=["Production & Stock"])


# ═══════════════════════════════════════════
# INCIDENTS
# ═══════════════════════════════════════════
@incidents_router.post("/", status_code=201)
def report_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    count = db.query(func.count(Incident.id)).scalar()
    incident = Incident(
        **data.model_dump(),
        incident_code=generate_code("INC", count + 1),
        reported_at=datetime.now(timezone.utc),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return {"incident_code": incident.incident_code, "id": incident.id}


@incidents_router.get("/")
def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    incident_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Incident)
    if status:
        q = q.filter(Incident.status == status)
    if severity:
        q = q.filter(Incident.severity == severity)
    if incident_type:
        q = q.filter(Incident.incident_type == incident_type)
    return q.order_by(Incident.reported_at.desc()).limit(100).all()


@incidents_router.get("/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(404, "Incident not found")
    actions = db.query(IncidentAction).filter(IncidentAction.incident_id == incident_id).order_by(IncidentAction.action_date).all()
    return {"incident": inc, "actions": actions, "total_action_cost": sum(a.cost for a in actions)}


@incidents_router.post("/actions", status_code=201)
def add_action(data: IncidentActionCreate, db: Session = Depends(get_db)):
    action = IncidentAction(**data.model_dump())
    db.add(action)
    db.commit()
    return {"id": action.id, "message": "Action recorded"}


@incidents_router.put("/{incident_id}/resolve")
def resolve_incident(incident_id: int, summary: str, preventive: str = None, actual_loss: float = 0, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(404, "Incident not found")
    inc.status = "resolved"
    inc.resolved_at = datetime.now(timezone.utc)
    inc.resolution_summary = summary
    inc.preventive_measures = preventive
    inc.actual_loss = actual_loss
    db.commit()
    return {"message": f"Incident {inc.incident_code} resolved"}


# ── Maintenance ──
@incidents_router.get("/maintenance/upcoming")
def upcoming_maintenance(days: int = 7, db: Session = Depends(get_db)):
    from datetime import timedelta
    cutoff = date.today() + timedelta(days=days)
    return db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.next_due <= cutoff,
        MaintenanceSchedule.status.in_(["scheduled", "overdue"]),
    ).order_by(MaintenanceSchedule.next_due).all()


@incidents_router.post("/maintenance", status_code=201)
def create_maintenance(data: MaintenanceCreate, db: Session = Depends(get_db)):
    ms = MaintenanceSchedule(**data.model_dump())
    db.add(ms)
    db.commit()
    return {"id": ms.id}


@incidents_router.put("/maintenance/{ms_id}/complete")
def complete_maintenance(ms_id: int, actual_cost: float = 0, notes: str = None, db: Session = Depends(get_db)):
    ms = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == ms_id).first()
    if not ms:
        raise HTTPException(404, "Schedule not found")
    ms.status = "completed"
    ms.last_performed = date.today()
    ms.actual_cost = actual_cost
    ms.completion_notes = notes
    # Calculate next due based on frequency
    freq_map = {"daily": 1, "weekly": 7, "monthly": 30, "quarterly": 90, "semi_annual": 180, "annual": 365}
    delta = freq_map.get(ms.frequency, 30)
    from datetime import timedelta
    ms.next_due = date.today() + timedelta(days=delta)
    db.commit()
    return {"message": "Maintenance completed", "next_due": str(ms.next_due)}


# ═══════════════════════════════════════════
# PRODUCTION
# ═══════════════════════════════════════════
@production_router.post("/batches", status_code=201)
def create_production_batch(data: ProductionBatchCreate, db: Session = Depends(get_db)):
    batch = ProductionBatch(**data.model_dump(), final_quantity=data.raw_quantity)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {"batch_code": batch.batch_code, "id": batch.id}


@production_router.get("/batches")
def list_production_batches(
    category: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(ProductionBatch)
    if category:
        q = q.filter(ProductionBatch.category == category)
    if status:
        q = q.filter(ProductionBatch.status == status)
    if start_date:
        q = q.filter(ProductionBatch.production_date >= start_date)
    return q.order_by(ProductionBatch.production_date.desc()).limit(100).all()


@production_router.post("/processing", status_code=201)
def log_processing(data: ProcessingLogCreate, db: Session = Depends(get_db)):
    log = ProcessingLog(**data.model_dump())
    db.add(log)
    db.commit()
    return {"id": log.id}


@production_router.post("/packaging", status_code=201)
def log_packaging(data: PackagingLogCreate, db: Session = Depends(get_db)):
    log = PackagingLog(**data.model_dump())
    db.add(log)
    batch = db.query(ProductionBatch).filter(ProductionBatch.id == data.batch_id).first()
    if batch:
        batch.status = "packaged"
    db.commit()
    return {"id": log.id}


@production_router.post("/quality-checks", status_code=201)
def log_quality_check(data: QualityCheckCreate, db: Session = Depends(get_db)):
    qc = QualityCheck(**data.model_dump())
    db.add(qc)
    db.commit()
    return {"id": qc.id, "result": qc.result}


# ── Stock Ledger ──
@production_router.get("/stock-ledger")
def get_stock_ledger(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(StockLedger)
    if category:
        q = q.filter(StockLedger.category == category)
    return q.order_by(StockLedger.product).all()


@production_router.post("/stock-movements", status_code=201)
def log_stock_movement(data: StockMovementCreate, db: Session = Depends(get_db)):
    movement = StockMovement(**data.model_dump(), total_value=data.quantity * data.unit_cost)
    db.add(movement)
    # Update stock ledger
    ledger = db.query(StockLedger).filter(StockLedger.product == data.product).first()
    if not ledger:
        ledger = StockLedger(product=data.product, category="general", unit=data.unit, location=data.to_location or "packhouse")
        db.add(ledger)
        db.flush()
    if data.movement_type.endswith("_in"):
        ledger.current_stock += data.quantity
        ledger.last_in_date = data.movement_date
    elif data.movement_type.endswith("_out"):
        ledger.current_stock = max(0, ledger.current_stock - data.quantity)
        ledger.last_out_date = data.movement_date
    ledger.total_value = ledger.current_stock * ledger.avg_cost_per_unit
    db.commit()
    return {"id": movement.id, "stock_after": ledger.current_stock}


@production_router.get("/stock-movements")
def list_stock_movements(
    product: Optional[str] = None,
    movement_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(StockMovement)
    if product:
        q = q.filter(StockMovement.product == product)
    if movement_type:
        q = q.filter(StockMovement.movement_type == movement_type)
    if start_date:
        q = q.filter(StockMovement.movement_date >= start_date)
    if end_date:
        q = q.filter(StockMovement.movement_date <= end_date)
    return q.order_by(StockMovement.movement_date.desc()).limit(200).all()
