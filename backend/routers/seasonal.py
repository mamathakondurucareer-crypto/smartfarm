"""Seasonal Operations Scheduler — monthly tasks and crop rotation plans."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.seasonal_calendar import SeasonalTask, SeasonalTaskCompletion, CropRotationPlan
from backend.schemas import (
    SeasonalTaskCreate, SeasonalTaskOut,
    SeasonalTaskCompletionCreate, SeasonalTaskCompletionOut,
    CropRotationPlanCreate, CropRotationPlanOut,
)

router = APIRouter(prefix="/api/seasonal", tags=["Seasonal Calendar"])

_WRITE_ROLES = ("admin", "manager", "supervisor")


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Seasonal Tasks ────────────────────────────────────────────────────────────

@router.post("/tasks", response_model=SeasonalTaskOut)
def create_task(
    data: SeasonalTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    if not (1 <= data.month <= 12):
        raise HTTPException(400, "month must be between 1 and 12")
    task = SeasonalTask(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=list[SeasonalTaskOut])
def list_tasks(
    month: Optional[int] = None,
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SeasonalTask)
    if active_only:
        q = q.filter(SeasonalTask.is_active == True)
    if month is not None:
        q = q.filter(SeasonalTask.month == month)
    if category:
        q = q.filter(SeasonalTask.category == category)
    return q.order_by(SeasonalTask.month, SeasonalTask.week).all()


@router.get("/tasks/current-month", response_model=list[SeasonalTaskOut])
def current_month_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all active tasks for the current calendar month."""
    current_month = date.today().month
    return (
        db.query(SeasonalTask)
        .filter(SeasonalTask.month == current_month, SeasonalTask.is_active == True)
        .order_by(SeasonalTask.week)
        .all()
    )


@router.get("/tasks/upcoming")
def upcoming_tasks(
    days_ahead: int = Query(default=60, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tasks spanning the next N days (across current and next month)."""
    today = date.today()
    months_covered: set[int] = set()
    for offset in range(0, days_ahead + 1, 1):
        from datetime import timedelta
        d = today + timedelta(days=offset)
        months_covered.add(d.month)

    tasks = (
        db.query(SeasonalTask)
        .filter(SeasonalTask.month.in_(list(months_covered)), SeasonalTask.is_active == True)
        .order_by(SeasonalTask.month, SeasonalTask.week)
        .all()
    )

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    }

    grouped: dict = {}
    for t in tasks:
        mn = month_names[t.month]
        if mn not in grouped:
            grouped[mn] = []
        grouped[mn].append({
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "week": t.week,
            "assigned_to": t.assigned_to,
        })

    return {"days_ahead": days_ahead, "months_covered": sorted(months_covered), "tasks_by_month": grouped}


# ── Task Completions ──────────────────────────────────────────────────────────

@router.post("/completions", response_model=SeasonalTaskCompletionOut)
def log_completion(
    data: SeasonalTaskCompletionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(SeasonalTask).filter(SeasonalTask.id == data.task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    completion = SeasonalTaskCompletion(**data.model_dump(), completed_by=current_user.id)
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion


@router.get("/completions")
def list_completions(
    year: int = Query(default=2025),
    month: Optional[int] = None,
    task_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SeasonalTaskCompletion).filter(SeasonalTaskCompletion.year == year)
    if task_id:
        q = q.filter(SeasonalTaskCompletion.task_id == task_id)
    completions = q.order_by(SeasonalTaskCompletion.completion_date).all()

    if month is not None:
        completions = [c for c in completions if c.completion_date.month == month]

    return completions


# ── Crop Rotation Plans ───────────────────────────────────────────────────────

@router.post("/crop-rotation", response_model=CropRotationPlanOut)
def create_rotation_plan(
    data: CropRotationPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    plan = CropRotationPlan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/crop-rotation", response_model=list[CropRotationPlanOut])
def list_rotation_plans(
    year: Optional[int] = None,
    field_or_zone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(CropRotationPlan)
    if year:
        q = q.filter(CropRotationPlan.year == year)
    if field_or_zone:
        q = q.filter(CropRotationPlan.field_or_zone.ilike(f"%{field_or_zone}%"))
    return q.order_by(CropRotationPlan.year, CropRotationPlan.sowing_month).all()
