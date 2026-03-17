"""Expansion Planning module — phases, milestones, CapEx tracking, readiness score."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.expansion import ExpansionPhase, ExpansionMilestone, ExpansionCapex
from backend.schemas import (
    ExpansionPhaseCreate, ExpansionPhaseOut,
    ExpansionMilestoneCreate, ExpansionMilestoneOut,
    ExpansionCapexCreate, ExpansionCapexOut,
)

router = APIRouter(prefix="/api/expansion", tags=["Expansion Planning"])

_WRITE_ROLES = ("admin", "manager")


def _can_write(u: User) -> bool:
    return u.role.name in _WRITE_ROLES


# ── Phases ────────────────────────────────────────────────────────────────────

@router.post("/phases", response_model=ExpansionPhaseOut)
def create_phase(
    data: ExpansionPhaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    phase = ExpansionPhase(**data.model_dump())
    db.add(phase)
    db.commit()
    db.refresh(phase)
    return phase


@router.get("/phases", response_model=list[ExpansionPhaseOut])
def list_phases(
    year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ExpansionPhase)
    if year:
        q = q.filter(ExpansionPhase.year == year)
    if status:
        q = q.filter(ExpansionPhase.status == status)
    return q.order_by(ExpansionPhase.year, ExpansionPhase.planned_start).all()


@router.put("/phases/{phase_id}/status")
def update_phase_status(
    phase_id: int,
    status: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    phase = db.query(ExpansionPhase).filter(ExpansionPhase.id == phase_id).first()
    if not phase:
        raise HTTPException(404, "Phase not found")
    phase.status = status
    if status == "in_progress" and not phase.actual_start:
        phase.actual_start = date.today()
    elif status == "completed" and not phase.actual_end:
        phase.actual_end = date.today()
    db.commit()
    return {"id": phase_id, "status": status}


# ── Milestones ────────────────────────────────────────────────────────────────

@router.post("/milestones", response_model=ExpansionMilestoneOut)
def create_milestone(
    data: ExpansionMilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    phase = db.query(ExpansionPhase).filter(ExpansionPhase.id == data.phase_id).first()
    if not phase:
        raise HTTPException(404, "Phase not found")
    ms = ExpansionMilestone(**data.model_dump())
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms


@router.get("/milestones", response_model=list[ExpansionMilestoneOut])
def list_milestones(
    phase_id: Optional[int] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ExpansionMilestone)
    if phase_id:
        q = q.filter(ExpansionMilestone.phase_id == phase_id)
    if is_completed is not None:
        q = q.filter(ExpansionMilestone.is_completed == is_completed)
    return q.order_by(ExpansionMilestone.phase_id, ExpansionMilestone.sort_order, ExpansionMilestone.due_date).all()


@router.put("/milestones/{milestone_id}/complete")
def complete_milestone(
    milestone_id: int,
    completion_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ms = db.query(ExpansionMilestone).filter(ExpansionMilestone.id == milestone_id).first()
    if not ms:
        raise HTTPException(404, "Milestone not found")
    ms.is_completed = True
    ms.completed_date = date.today()
    ms.completed_by = current_user.id
    if completion_notes:
        ms.completion_notes = completion_notes
    db.commit()
    return {"id": milestone_id, "is_completed": True, "completed_date": ms.completed_date}


# ── CapEx ─────────────────────────────────────────────────────────────────────

@router.post("/capex", response_model=ExpansionCapexOut)
def create_capex(
    data: ExpansionCapexCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not _can_write(current_user):
        raise HTTPException(403, "Insufficient permissions")
    capex_data = data.model_dump()
    net_cost = round(capex_data.get("actual_amount", 0) - capex_data.get("subsidy_amount", 0), 2)
    capex_data["net_cost"] = net_cost
    capex = ExpansionCapex(**capex_data)
    db.add(capex)

    # Update phase total_spent
    phase = db.query(ExpansionPhase).filter(ExpansionPhase.id == data.phase_id).first()
    if phase:
        phase.total_spent = round(phase.total_spent + data.actual_amount, 2)

    db.commit()
    db.refresh(capex)
    return capex


@router.get("/capex", response_model=list[ExpansionCapexOut])
def list_capex(
    phase_id: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ExpansionCapex)
    if phase_id:
        q = q.filter(ExpansionCapex.phase_id == phase_id)
    if category:
        q = q.filter(ExpansionCapex.category == category)
    return q.order_by(ExpansionCapex.phase_id, ExpansionCapex.category).all()


@router.get("/capex/budget-vs-actual")
def capex_budget_vs_actual(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """CapEx budget vs actuals grouped by phase and category."""
    phases = db.query(ExpansionPhase).order_by(ExpansionPhase.year).all()
    result = []
    for phase in phases:
        items = db.query(ExpansionCapex).filter(ExpansionCapex.phase_id == phase.id).all()
        total_budgeted = round(sum(i.budgeted_amount for i in items), 2)
        total_actual = round(sum(i.actual_amount for i in items), 2)
        total_subsidy = round(sum(i.subsidy_amount for i in items), 2)
        total_net = round(sum(i.net_cost for i in items), 2)

        by_category: dict = {}
        for item in items:
            cat = item.category
            if cat not in by_category:
                by_category[cat] = {"budgeted": 0.0, "actual": 0.0}
            by_category[cat]["budgeted"] = round(by_category[cat]["budgeted"] + item.budgeted_amount, 2)
            by_category[cat]["actual"] = round(by_category[cat]["actual"] + item.actual_amount, 2)

        result.append({
            "phase_id": phase.id,
            "phase_name": phase.name,
            "year": phase.year,
            "status": phase.status,
            "total_budgeted": total_budgeted,
            "total_actual": total_actual,
            "total_subsidy": total_subsidy,
            "total_net_cost": total_net,
            "variance": round(total_actual - total_budgeted, 2),
            "by_category": by_category,
        })
    return result


# ── Timeline + Readiness ──────────────────────────────────────────────────────

@router.get("/timeline")
def expansion_timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Expansion timeline with milestone completion status per phase."""
    phases = db.query(ExpansionPhase).order_by(ExpansionPhase.year, ExpansionPhase.planned_start).all()
    timeline = []
    for phase in phases:
        milestones = db.query(ExpansionMilestone).filter(
            ExpansionMilestone.phase_id == phase.id
        ).order_by(ExpansionMilestone.sort_order, ExpansionMilestone.due_date).all()

        total = len(milestones)
        done = sum(1 for m in milestones if m.is_completed)
        pct = round(done / total * 100, 1) if total else 0.0

        timeline.append({
            "phase_id": phase.id,
            "name": phase.name,
            "year": phase.year,
            "status": phase.status,
            "planned_start": phase.planned_start,
            "planned_end": phase.planned_end,
            "actual_start": phase.actual_start,
            "actual_end": phase.actual_end,
            "total_budget": phase.total_budget,
            "total_spent": phase.total_spent,
            "milestone_total": total,
            "milestone_completed": done,
            "completion_pct": pct,
            "milestones": [
                {
                    "id": m.id,
                    "title": m.title,
                    "due_date": m.due_date,
                    "completed_date": m.completed_date,
                    "is_completed": m.is_completed,
                    "priority": m.priority,
                }
                for m in milestones
            ],
        })
    return timeline


@router.get("/readiness-score")
def expansion_readiness_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Expansion readiness score based on milestone and CapEx completion."""
    phases = db.query(ExpansionPhase).all()
    milestones = db.query(ExpansionMilestone).all()
    total_ms = len(milestones)
    done_ms = sum(1 for m in milestones if m.is_completed)
    ms_score = round(done_ms / total_ms * 100, 1) if total_ms else 0.0

    total_budget = sum(p.total_budget for p in phases)
    total_spent = sum(p.total_spent for p in phases)
    capex_pct = round(total_spent / total_budget * 100, 1) if total_budget else 0.0

    overall = round((ms_score + min(capex_pct, 100)) / 2, 1)

    return {
        "milestone_completion_pct": ms_score,
        "capex_utilisation_pct": capex_pct,
        "overall_readiness_score": overall,
        "total_milestones": total_ms,
        "completed_milestones": done_ms,
        "total_budget": round(total_budget, 2),
        "total_spent": round(total_spent, 2),
    }
