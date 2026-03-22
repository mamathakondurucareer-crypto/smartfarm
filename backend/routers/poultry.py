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
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import (
    EggCollectionCreate, PoultryFeedLogCreate, PoultryHealthLogCreate,
    PoultryFlockUpdate, DuckFlockUpdate, BeeHiveUpdate,
)

router = APIRouter(prefix="/api/poultry", tags=["Poultry & Livestock"])

_WRITE_ROLES = ("admin", "manager", "operator")


@router.get("/flocks")
def list_flocks(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(PoultryFlock).order_by(PoultryFlock.id).limit(200).all()


@router.get("/flocks/{flock_id}")
def get_flock(flock_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
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
def log_egg_collection(
    data: EggCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to log egg collections")
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
def list_egg_collections(
    flock_id: Optional[int] = None,
    start_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(EggCollection)
    if flock_id:
        q = q.filter(EggCollection.flock_id == flock_id)
    if start_date:
        q = q.filter(EggCollection.collection_date >= start_date)
    return q.order_by(EggCollection.collection_date.desc()).limit(90).all()


@router.post("/feed", status_code=201)
def log_poultry_feed(
    data: PoultryFeedLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to log poultry feed")
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
def log_health(
    data: PoultryHealthLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to log poultry health")
    log = PoultryHealthLog(**data.model_dump())
    db.add(log)
    if data.mortality_count > 0:
        flock = db.query(PoultryFlock).filter(PoultryFlock.id == data.flock_id).first()
        if flock:
            flock.current_count = max(0, flock.current_count - data.mortality_count)
            flock.total_mortality += data.mortality_count
    db.commit()
    return {"id": log.id, "message": "Health log recorded"}


@router.put("/flocks/{flock_id}")
def update_flock(
    flock_id: int,
    data: PoultryFlockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to update flocks")
    flock = db.query(PoultryFlock).filter(PoultryFlock.id == flock_id).first()
    if not flock:
        raise HTTPException(404, "Flock not found")
    if data.current_count is not None:
        flock.current_count = data.current_count
    if data.lay_rate_pct is not None:
        flock.lay_rate_pct = data.lay_rate_pct
    if data.total_eggs_produced is not None:
        flock.total_eggs_produced = data.total_eggs_produced
    if data.status is not None:
        flock.status = data.status
    db.commit()
    return {"message": "Flock updated", "flock_id": flock_id}


# ── Ducks ──
@router.get("/ducks")
def list_ducks(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(DuckFlock).order_by(DuckFlock.id).limit(200).all()


@router.put("/ducks/{duck_id}")
def update_duck_flock(
    duck_id: int,
    data: DuckFlockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to update duck flocks")
    duck = db.query(DuckFlock).filter(DuckFlock.id == duck_id).first()
    if not duck:
        raise HTTPException(404, "Duck flock not found")
    if data.current_count is not None:
        duck.current_count = data.current_count
    if data.eggs_today is not None:
        duck.eggs_today = data.eggs_today
    if data.deployment_area is not None:
        duck.deployment_area = data.deployment_area
    db.commit()
    return {"message": "Duck flock updated", "duck_id": duck_id}


# ── Bees ──
@router.get("/bees")
def list_hives(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(BeeHive).order_by(BeeHive.id).limit(200).all()


@router.put("/bees/{hive_id}")
def update_hive(
    hive_id: int,
    data: BeeHiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to update hives")
    hive = db.query(BeeHive).filter(BeeHive.id == hive_id).first()
    if not hive:
        raise HTTPException(404, "Hive not found")
    if data.colony_strength is not None:
        hive.colony_strength = data.colony_strength
    if data.total_honey_harvested_kg is not None:
        hive.total_honey_harvested_kg = data.total_honey_harvested_kg
    if data.last_inspection_date is not None:
        hive.last_inspection_date = data.last_inspection_date
    if data.status is not None:
        hive.status = data.status
    db.commit()
    return {"message": "Hive updated", "hive_id": hive_id}


@router.get("/bees/{hive_id}")
def get_hive(
    hive_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    hive = db.query(BeeHive).filter(BeeHive.id == hive_id).first()
    if not hive:
        raise HTTPException(404, "Hive not found")
    harvests = db.query(HoneyHarvest).filter(HoneyHarvest.hive_id == hive_id).order_by(HoneyHarvest.harvest_date.desc()).limit(10).all()
    return {"hive": hive, "recent_harvests": harvests}
