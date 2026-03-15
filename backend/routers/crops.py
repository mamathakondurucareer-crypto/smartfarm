"""Crop management endpoints: greenhouse, vertical farm, field crops, activities, harvests, disease."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.crop import (
    GreenhouseCrop, VerticalFarmBatch, FieldCrop,
    CropActivity, CropHarvest, CropDisease,
)
from backend.schemas import (
    GreenhouseCropCreate, GreenhouseCropOut, VerticalFarmBatchCreate,
    CropActivityCreate, CropHarvestCreate, CropDiseaseCreate,
)

router = APIRouter(prefix="/api/crops", tags=["Crop Management"])


# ── Greenhouse ──
@router.get("/greenhouse")
def list_greenhouse_crops(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(GreenhouseCrop).filter(GreenhouseCrop.is_active == True)
    if status:
        q = q.filter(GreenhouseCrop.status == status)
    return q.all()


@router.post("/greenhouse", status_code=201)
def create_greenhouse_crop(data: GreenhouseCropCreate, db: Session = Depends(get_db)):
    crop = GreenhouseCrop(**data.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return GreenhouseCropOut.model_validate(crop)


@router.put("/greenhouse/{crop_id}/stage")
def update_growth_stage(crop_id: int, stage: str, health_score: float = None, db: Session = Depends(get_db)):
    crop = db.query(GreenhouseCrop).filter(GreenhouseCrop.id == crop_id).first()
    if not crop:
        raise HTTPException(404, "Crop not found")
    crop.growth_stage = stage
    if health_score is not None:
        crop.health_score = health_score
    db.commit()
    return {"message": "Stage updated", "crop_code": crop.crop_code, "stage": stage}


# ── Vertical Farm ──
@router.get("/vertical-farm")
def list_vf_batches(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(VerticalFarmBatch)
    if status:
        q = q.filter(VerticalFarmBatch.status == status)
    return q.order_by(VerticalFarmBatch.seeding_date.desc()).all()


@router.post("/vertical-farm", status_code=201)
def create_vf_batch(data: VerticalFarmBatchCreate, db: Session = Depends(get_db)):
    batch = VerticalFarmBatch(**data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


# ── Field Crops ──
@router.get("/field-crops")
def list_field_crops(db: Session = Depends(get_db)):
    return db.query(FieldCrop).filter(FieldCrop.is_active == True).all()


# ── Activities ──
@router.post("/activities", status_code=201)
def log_activity(data: CropActivityCreate, db: Session = Depends(get_db)):
    activity = CropActivity(**data.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return {"id": activity.id, "message": "Activity logged"}


@router.get("/activities")
def list_activities(
    crop_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(CropActivity)
    if crop_id:
        q = q.filter(CropActivity.greenhouse_crop_id == crop_id)
    if start_date:
        q = q.filter(CropActivity.activity_date >= start_date)
    if end_date:
        q = q.filter(CropActivity.activity_date <= end_date)
    return q.order_by(CropActivity.activity_date.desc()).limit(200).all()


# ── Harvests ──
@router.post("/harvests", status_code=201)
def log_crop_harvest(data: CropHarvestCreate, db: Session = Depends(get_db)):
    harvest = CropHarvest(
        **data.model_dump(),
        total_revenue=data.quantity_kg * data.sale_price_per_kg,
    )
    db.add(harvest)
    # Update crop yield
    if data.greenhouse_crop_id:
        crop = db.query(GreenhouseCrop).filter(GreenhouseCrop.id == data.greenhouse_crop_id).first()
        if crop:
            crop.actual_yield_kg += data.quantity_kg
    if data.vf_batch_id:
        vf = db.query(VerticalFarmBatch).filter(VerticalFarmBatch.id == data.vf_batch_id).first()
        if vf:
            vf.actual_yield_kg += data.quantity_kg
    db.commit()
    db.refresh(harvest)
    return {"id": harvest.id, "total_revenue": harvest.total_revenue}


# ── Disease ──
@router.post("/diseases", status_code=201)
def report_disease(data: CropDiseaseCreate, db: Session = Depends(get_db)):
    disease = CropDisease(**data.model_dump())
    db.add(disease)
    # Reduce health score
    if data.greenhouse_crop_id:
        crop = db.query(GreenhouseCrop).filter(GreenhouseCrop.id == data.greenhouse_crop_id).first()
        if crop:
            impact = {"mild": 5, "moderate": 15, "severe": 30}.get(data.severity, 10)
            crop.health_score = max(0, crop.health_score - impact)
    db.commit()
    db.refresh(disease)
    return {"id": disease.id, "message": "Disease reported"}


@router.get("/diseases")
def list_diseases(outcome: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(CropDisease)
    if outcome:
        q = q.filter(CropDisease.outcome == outcome)
    return q.order_by(CropDisease.detected_date.desc()).limit(100).all()
