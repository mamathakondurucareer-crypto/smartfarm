"""Poultry, duck, and bee management endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.poultry import (
    PoultryFlock, EggCollection, DuckFlock, BeeHive, HoneyHarvest,
    PoultryFeedLog, PoultryHealthLog,
)
from backend.schemas import EggCollectionCreate, PoultryFeedLogCreate, PoultryHealthLogCreate

router = APIRouter(prefix="/api/poultry", tags=["Poultry & Livestock"])


@router.get("/flocks")
def list_flocks(db: Session = Depends(get_db)):
    return db.query(PoultryFlock).all()


@router.get("/flocks/{flock_id}")
def get_flock(flock_id: int, db: Session = Depends(get_db)):
    flock = db.query(PoultryFlock).filter(PoultryFlock.id == flock_id).first()
    if not flock:
        raise HTTPException(404, "Flock not found")
    today_eggs = db.query(EggCollection).filter(
        EggCollection.flock_id == flock_id, EggCollection.collection_date == date.today()
    ).first()
    return {
        "flock": flock,
        "eggs_today": today_eggs.total_eggs if today_eggs else 0,
        "broken_today": today_eggs.broken_eggs if today_eggs else 0,
    }


@router.post("/eggs", status_code=201)
def log_egg_collection(data: EggCollectionCreate, db: Session = Depends(get_db)):
    flock = db.query(PoultryFlock).filter(PoultryFlock.id == data.flock_id).first()
    if not flock:
        raise HTTPException(404, "Flock not found")
    sellable = data.total_eggs - data.broken_eggs - data.dirty_eggs
    revenue = sellable * data.sale_price_per_egg
    collection = EggCollection(**data.model_dump(), revenue=revenue, eggs_sold=sellable)
    db.add(collection)
    flock.total_eggs_produced += data.total_eggs
    flock.lay_rate_pct = round((data.total_eggs / flock.current_count) * 100, 1) if flock.current_count > 0 else 0
    db.commit()
    db.refresh(collection)
    return {"id": collection.id, "sellable_eggs": sellable, "revenue": revenue}


@router.get("/eggs")
def list_egg_collections(flock_id: Optional[int] = None, start_date: Optional[date] = None, db: Session = Depends(get_db)):
    q = db.query(EggCollection)
    if flock_id:
        q = q.filter(EggCollection.flock_id == flock_id)
    if start_date:
        q = q.filter(EggCollection.collection_date >= start_date)
    return q.order_by(EggCollection.collection_date.desc()).limit(90).all()


@router.post("/feed", status_code=201)
def log_poultry_feed(data: PoultryFeedLogCreate, db: Session = Depends(get_db)):
    flock = db.query(PoultryFlock).filter(PoultryFlock.id == data.flock_id).first()
    if not flock:
        raise HTTPException(404, "Flock not found")
    log = PoultryFeedLog(
        **data.model_dump(),
        feed_per_bird_g=round((data.quantity_kg * 1000) / flock.current_count, 1) if flock.current_count > 0 else 0,
    )
    db.add(log)
    db.commit()
    return {"id": log.id, "feed_per_bird_g": log.feed_per_bird_g}


@router.post("/health", status_code=201)
def log_health(data: PoultryHealthLogCreate, db: Session = Depends(get_db)):
    log = PoultryHealthLog(**data.model_dump())
    db.add(log)
    if data.mortality_count > 0:
        flock = db.query(PoultryFlock).filter(PoultryFlock.id == data.flock_id).first()
        if flock:
            flock.current_count = max(0, flock.current_count - data.mortality_count)
            flock.total_mortality += data.mortality_count
    db.commit()
    return {"id": log.id, "message": "Health log recorded"}


# ── Ducks ──
@router.get("/ducks")
def list_ducks(db: Session = Depends(get_db)):
    return db.query(DuckFlock).all()


# ── Bees ──
@router.get("/bees")
def list_hives(db: Session = Depends(get_db)):
    return db.query(BeeHive).all()


@router.get("/bees/{hive_id}")
def get_hive(hive_id: int, db: Session = Depends(get_db)):
    hive = db.query(BeeHive).filter(BeeHive.id == hive_id).first()
    if not hive:
        raise HTTPException(404, "Hive not found")
    harvests = db.query(HoneyHarvest).filter(HoneyHarvest.hive_id == hive_id).order_by(HoneyHarvest.harvest_date.desc()).limit(10).all()
    return {"hive": hive, "recent_harvests": harvests}
