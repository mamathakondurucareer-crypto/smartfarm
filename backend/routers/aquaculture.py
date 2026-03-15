"""Aquaculture endpoints: ponds, fish batches, feeding, water quality, harvests."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.aquaculture import Pond, FishBatch, FeedLog, WaterQualityLog, FishHarvest, CrabBatch
from backend.schemas import (
    PondCreate, PondOut, FishBatchCreate, FishBatchOut,
    FeedLogCreate, WaterQualityCreate, FishHarvestCreate,
)
from backend.services.alert_service import check_threshold

router = APIRouter(prefix="/api/aquaculture", tags=["Aquaculture"])


# ── Ponds ──
@router.get("/ponds", response_model=list[PondOut])
def list_ponds(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Pond).filter(Pond.is_active == True)
    if status:
        q = q.filter(Pond.status == status)
    return q.order_by(Pond.pond_code).all()


@router.post("/ponds", response_model=PondOut, status_code=201)
def create_pond(data: PondCreate, db: Session = Depends(get_db)):
    pond = Pond(
        **data.model_dump(),
        area_sqm=data.length_m * data.width_m,
        volume_liters=data.length_m * data.width_m * data.depth_m * 1000,
    )
    db.add(pond)
    db.commit()
    db.refresh(pond)
    return pond


@router.get("/ponds/{pond_id}")
def get_pond(pond_id: int, db: Session = Depends(get_db)):
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(404, "Pond not found")
    batches = db.query(FishBatch).filter(FishBatch.pond_id == pond_id, FishBatch.status == "growing").all()
    total_stock = sum(b.current_count for b in batches)
    total_biomass = sum(b.current_count * b.current_avg_weight_g / 1000 for b in batches)
    latest_wq = db.query(WaterQualityLog).filter(
        WaterQualityLog.pond_id == pond_id
    ).order_by(WaterQualityLog.recorded_at.desc()).first()
    today_feed = db.query(func.coalesce(func.sum(FeedLog.quantity_kg), 0)).filter(
        FeedLog.pond_id == pond_id, FeedLog.feed_date == date.today()
    ).scalar()
    return {
        "pond": PondOut.model_validate(pond),
        "total_stock": total_stock,
        "total_biomass_kg": round(total_biomass, 1),
        "today_feed_kg": float(today_feed),
        "latest_water_quality": {
            "do": latest_wq.dissolved_oxygen if latest_wq else None,
            "ph": latest_wq.ph if latest_wq else None,
            "temp": latest_wq.water_temperature if latest_wq else None,
            "ammonia": latest_wq.ammonia if latest_wq else None,
        } if latest_wq else None,
        "batches": [FishBatchOut.model_validate(b) for b in batches],
    }


# ── Fish Batches ──
@router.post("/batches", response_model=FishBatchOut, status_code=201)
def create_batch(data: FishBatchCreate, db: Session = Depends(get_db)):
    pond = db.query(Pond).filter(Pond.id == data.pond_id).first()
    if not pond:
        raise HTTPException(404, "Pond not found")
    batch = FishBatch(
        **data.model_dump(),
        current_count=data.initial_count,
        current_avg_weight_g=data.initial_avg_weight_g,
        total_cost=data.initial_count * data.cost_per_fingerling,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/batches")
def list_batches(pond_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(FishBatch)
    if pond_id:
        q = q.filter(FishBatch.pond_id == pond_id)
    if status:
        q = q.filter(FishBatch.status == status)
    return q.order_by(FishBatch.stocking_date.desc()).all()


@router.put("/batches/{batch_id}/update-weight")
def update_batch_weight(batch_id: int, avg_weight_g: float, mortality_count: int = 0, db: Session = Depends(get_db)):
    batch = db.query(FishBatch).filter(FishBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")
    batch.current_avg_weight_g = avg_weight_g
    if mortality_count > 0:
        batch.mortality_count += mortality_count
        batch.current_count = max(0, batch.current_count - mortality_count)
    # Recalculate FCR
    total_feed = db.query(func.coalesce(func.sum(FeedLog.quantity_kg), 0)).filter(
        FeedLog.pond_id == batch.pond_id
    ).scalar()
    biomass_gain = (batch.current_count * batch.current_avg_weight_g - batch.initial_count * batch.initial_avg_weight_g) / 1000
    batch.fcr = round(float(total_feed) / biomass_gain, 2) if biomass_gain > 0 else 0
    db.commit()
    return {"message": "Batch updated", "current_count": batch.current_count, "fcr": batch.fcr}


# ── Feed Logs ──
@router.post("/feed-logs", status_code=201)
def log_feed(data: FeedLogCreate, db: Session = Depends(get_db)):
    log = FeedLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"id": log.id, "message": "Feed logged", "total_cost": log.quantity_kg * log.cost_per_kg}


@router.get("/feed-logs")
def list_feed_logs(
    pond_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(FeedLog)
    if pond_id:
        q = q.filter(FeedLog.pond_id == pond_id)
    if start_date:
        q = q.filter(FeedLog.feed_date >= start_date)
    if end_date:
        q = q.filter(FeedLog.feed_date <= end_date)
    return q.order_by(FeedLog.feed_date.desc()).limit(200).all()


# ── Water Quality ──
@router.post("/water-quality", status_code=201)
def log_water_quality(data: WaterQualityCreate, db: Session = Depends(get_db)):
    log = WaterQualityLog(**data.model_dump())
    db.add(log)
    db.commit()
    # Check thresholds
    alerts = []
    pond = db.query(Pond).filter(Pond.id == data.pond_id).first()
    zone = pond.pond_code if pond else f"pond_{data.pond_id}"
    if data.dissolved_oxygen is not None:
        a = check_threshold(db, "dissolved_oxygen", data.dissolved_oxygen, zone)
        if a:
            alerts.append(a.message)
    if data.ammonia is not None:
        a = check_threshold(db, "ammonia", data.ammonia, zone)
        if a:
            alerts.append(a.message)
    if data.ph is not None:
        a = check_threshold(db, "ph", data.ph, zone)
        if a:
            alerts.append(a.message)
    return {"id": log.id, "alerts_triggered": alerts}


@router.get("/water-quality/{pond_id}/latest")
def latest_water_quality(pond_id: int, limit: int = 24, db: Session = Depends(get_db)):
    logs = db.query(WaterQualityLog).filter(
        WaterQualityLog.pond_id == pond_id
    ).order_by(WaterQualityLog.recorded_at.desc()).limit(limit).all()
    return logs


# ── Harvests ──
@router.post("/harvests", status_code=201)
def log_harvest(data: FishHarvestCreate, db: Session = Depends(get_db)):
    harvest = FishHarvest(
        **data.model_dump(),
        total_revenue=data.quantity_kg * data.sale_price_per_kg,
    )
    db.add(harvest)
    # Update batch
    batch = db.query(FishBatch).filter(FishBatch.id == data.batch_id).first()
    if batch:
        batch.current_count = max(0, batch.current_count - data.count)
        if data.harvest_type == "full":
            batch.status = "completed"
    db.commit()
    db.refresh(harvest)
    return {"id": harvest.id, "total_revenue": harvest.total_revenue}


@router.get("/harvests")
def list_harvests(start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db)):
    q = db.query(FishHarvest)
    if start_date:
        q = q.filter(FishHarvest.harvest_date >= start_date)
    if end_date:
        q = q.filter(FishHarvest.harvest_date <= end_date)
    return q.order_by(FishHarvest.harvest_date.desc()).limit(100).all()


# ── Summary ──
@router.get("/summary")
def aquaculture_summary(db: Session = Depends(get_db)):
    ponds = db.query(Pond).filter(Pond.is_active == True).all()
    batches = db.query(FishBatch).filter(FishBatch.status == "growing").all()
    total_stock = sum(b.current_count for b in batches)
    total_biomass = sum(b.current_count * b.current_avg_weight_g / 1000 for b in batches)
    today_feed = db.query(func.coalesce(func.sum(FeedLog.quantity_kg), 0)).filter(
        FeedLog.feed_date == date.today()
    ).scalar()
    return {
        "active_ponds": len([p for p in ponds if p.status == "active"]),
        "total_stock": total_stock,
        "total_biomass_kg": round(total_biomass, 1),
        "today_feed_kg": float(today_feed),
        "batches": len(batches),
        "species_breakdown": {},
    }
