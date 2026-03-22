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
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import (
    GreenhouseCropCreate, GreenhouseCropOut, VerticalFarmBatchCreate,
    CropActivityCreate, CropHarvestCreate, CropDiseaseCreate,
    GreenhouseCropUpdate, VerticalFarmBatchUpdate,
)

router = APIRouter(prefix="/api/crops", tags=["Crop Management"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


# ── Greenhouse ──
@router.get("/greenhouse")
def list_greenhouse_crops(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(GreenhouseCrop).filter(GreenhouseCrop.is_active == True)
    if status:
        q = q.filter(GreenhouseCrop.status == status)
    return q.order_by(GreenhouseCrop.id).limit(500).all()


@router.post("/greenhouse", status_code=201)
def create_greenhouse_crop(
    data: GreenhouseCropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to create greenhouse crops")
    crop = GreenhouseCrop(**data.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return GreenhouseCropOut.model_validate(crop)


@router.put("/greenhouse/{crop_id}/stage")
def update_growth_stage(
    crop_id: int,
    stage: str,
    health_score: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to update crop stage")
    crop = db.query(GreenhouseCrop).filter(GreenhouseCrop.id == crop_id).first()
    if not crop:
        raise HTTPException(404, "Crop not found")
    crop.growth_stage = stage
    if health_score is not None:
        if not 0 <= health_score <= 100:
            raise HTTPException(400, "health_score must be between 0 and 100")
        crop.health_score = health_score
    db.commit()
    return {"message": "Stage updated", "crop_code": crop.crop_code, "stage": stage}


@router.delete("/greenhouse/{crop_id}", status_code=204)
def delete_greenhouse_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to delete greenhouse crops")
    crop = db.query(GreenhouseCrop).filter(GreenhouseCrop.id == crop_id).first()
    if not crop:
        raise HTTPException(404, "Crop not found")
    crop.is_active = False  # Soft delete
    db.commit()


@router.put("/greenhouse/{crop_id}")
def update_greenhouse_crop(
    crop_id: int,
    data: GreenhouseCropUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to update greenhouse crops")
    crop = db.query(GreenhouseCrop).filter(GreenhouseCrop.id == crop_id).first()
    if not crop:
        raise HTTPException(404, "Crop not found")
    if data.crop_name is not None:
        crop.crop_name = data.crop_name
    if data.growth_stage is not None:
        crop.growth_stage = data.growth_stage
    if data.health_score is not None:
        if not 0 <= data.health_score <= 100:
            raise HTTPException(400, "health_score must be between 0 and 100")
        crop.health_score = data.health_score
    if data.actual_yield_kg is not None:
        if data.actual_yield_kg < 0:
            raise HTTPException(400, "actual_yield_kg cannot be negative")
        crop.actual_yield_kg = data.actual_yield_kg
    if data.target_yield_kg is not None:
        if data.target_yield_kg < 0:
            raise HTTPException(400, "target_yield_kg cannot be negative")
        crop.target_yield_kg = data.target_yield_kg
    db.commit()
    return {"message": "Crop updated", "crop_id": crop_id}


# ── Vertical Farm ──
@router.get("/vertical-farm")
def list_vf_batches(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(VerticalFarmBatch)
    if status:
        q = q.filter(VerticalFarmBatch.status == status)
    return q.order_by(VerticalFarmBatch.seeding_date.desc()).limit(200).all()


@router.post("/vertical-farm", status_code=201)
def create_vf_batch(
    data: VerticalFarmBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to create vertical farm batches")
    batch = VerticalFarmBatch(**data.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.put("/vertical-farm/{batch_id}")
def update_vf_batch(
    batch_id: int,
    data: VerticalFarmBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to update vertical farm batches")
    batch = db.query(VerticalFarmBatch).filter(VerticalFarmBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")
    if data.crop_name is not None:
        batch.crop_name = data.crop_name
    if data.tier is not None:
        batch.tier = data.tier
    if data.current_day is not None:
        batch.current_day = data.current_day
    if data.health_score is not None:
        if not 0 <= data.health_score <= 100:
            raise HTTPException(400, "health_score must be between 0 and 100")
        batch.health_score = data.health_score
    if data.expected_yield_kg is not None:
        if data.expected_yield_kg < 0:
            raise HTTPException(400, "expected_yield_kg cannot be negative")
        batch.expected_yield_kg = data.expected_yield_kg
    if data.status is not None:
        batch.status = data.status
    db.commit()
    return {"message": "VF batch updated", "batch_id": batch_id}


# ── Field Crops ──
@router.get("/field-crops")
def list_field_crops(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(FieldCrop).filter(FieldCrop.is_active == True).order_by(FieldCrop.id).limit(500).all()


# ── Activities ──
@router.post("/activities", status_code=201)
def log_activity(
    data: CropActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to log crop activities")
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
    _: User = Depends(get_current_user),
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
def log_crop_harvest(
    data: CropHarvestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to log crop harvests")
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
def report_disease(
    data: CropDiseaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in _WRITE_ROLES:
        raise HTTPException(403, "Insufficient role to report diseases")
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
def list_diseases(
    outcome: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(CropDisease)
    if outcome:
        q = q.filter(CropDisease.outcome == outcome)
    return q.order_by(CropDisease.detected_date.desc()).limit(100).all()
