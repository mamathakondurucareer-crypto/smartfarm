"""Audit log viewer and reporting calendar (schedule creation, manual triggers, history)."""

from datetime import date, datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routers.auth import get_current_user
from backend.models.user import User
from backend.models.audit import AuditLog, ReportSchedule, ReportExecution
from backend.schemas import (
    AuditLogOut,
    ReportScheduleCreate, ReportScheduleOut,
    ReportExecutionCreate, ReportExecutionOut,
)

router = APIRouter(prefix="/api/audit", tags=["Audit & Reporting"])

_ADMIN_ROLES = ("admin", "manager")


def _require_admin(current_user: User):
    if current_user.role.name not in _ADMIN_ROLES:
        raise HTTPException(403, "Insufficient permissions")


# ── Audit Log ─────────────────────────────────────────────────────────────────

@router.get("/logs", response_model=list[AuditLogOut])
def list_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(default=200, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    q = db.query(AuditLog)
    if user_id:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if resource:
        q = q.filter(AuditLog.resource == resource)
    if date_from:
        q = q.filter(AuditLog.timestamp >= datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc))
    if date_to:
        end = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc)
        q = q.filter(AuditLog.timestamp <= end)
    return q.order_by(AuditLog.timestamp.desc()).limit(limit).all()


# ── Report Schedules ──────────────────────────────────────────────────────────

@router.post("/schedules", response_model=ReportScheduleOut)
def create_report_schedule(
    data: ReportScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    schedule = ReportSchedule(**data.model_dump(), created_by=current_user.id)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=list[ReportScheduleOut])
def list_report_schedules(
    active_only: bool = True,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    q = db.query(ReportSchedule)
    if active_only:
        q = q.filter(ReportSchedule.is_active == True)
    if report_type:
        q = q.filter(ReportSchedule.report_type == report_type)
    return q.order_by(ReportSchedule.next_run_date).all()


@router.put("/schedules/{schedule_id}/toggle")
def toggle_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(404, "Report schedule not found")
    schedule.is_active = not schedule.is_active
    db.commit()
    return {"id": schedule_id, "is_active": schedule.is_active}


@router.put("/schedules/{schedule_id}/advance")
def advance_next_run(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Advance next_run_date based on frequency after a successful run."""
    _require_admin(current_user)
    schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(404, "Report schedule not found")

    freq_map = {"daily": 1, "weekly": 7, "monthly": 30, "quarterly": 90}
    days = freq_map.get(schedule.frequency, 7)
    schedule.next_run_date = date.today() + timedelta(days=days)
    db.commit()
    return {"id": schedule_id, "next_run_date": schedule.next_run_date}


# ── Report Executions ─────────────────────────────────────────────────────────

@router.post("/executions", response_model=ReportExecutionOut)
def trigger_report(
    data: ReportExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger a report execution (async processing handled externally)."""
    _require_admin(current_user)
    execution = ReportExecution(
        schedule_id=data.schedule_id,
        report_type=data.report_type,
        triggered_by="manual",
        started_at=datetime.now(tz=timezone.utc),
        status="running",
        requested_by=current_user.id,
        parameters=data.parameters,
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


@router.get("/executions", response_model=list[ReportExecutionOut])
def list_report_executions(
    schedule_id: Optional[int] = None,
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    q = db.query(ReportExecution)
    if schedule_id:
        q = q.filter(ReportExecution.schedule_id == schedule_id)
    if report_type:
        q = q.filter(ReportExecution.report_type == report_type)
    if status:
        q = q.filter(ReportExecution.status == status)
    if date_from:
        q = q.filter(ReportExecution.started_at >= datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc))
    return q.order_by(ReportExecution.started_at.desc()).limit(limit).all()


@router.patch("/executions/{execution_id}/complete")
def complete_execution(
    execution_id: int,
    status: str = Query(..., description="success | failed"),
    file_url: Optional[str] = Query(default=None),
    error_message: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    if status not in ("success", "failed"):
        raise HTTPException(400, "status must be 'success' or 'failed'")
    execution = db.query(ReportExecution).filter(ReportExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(404, "Execution not found")
    execution.status = status
    execution.completed_at = datetime.now(tz=timezone.utc)
    if file_url:
        execution.file_url = file_url
    if error_message:
        execution.error_message = error_message
    db.commit()
    db.refresh(execution)
    return execution


@router.get("/calendar")
def reporting_calendar(
    days_ahead: int = Query(default=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upcoming report due dates within the next N days."""
    _require_admin(current_user)
    cutoff = date.today() + timedelta(days=days_ahead)
    schedules = db.query(ReportSchedule).filter(
        ReportSchedule.is_active == True,
        ReportSchedule.next_run_date <= cutoff,
    ).order_by(ReportSchedule.next_run_date).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "report_type": s.report_type,
            "frequency": s.frequency,
            "next_run_date": s.next_run_date,
            "output_format": s.output_format,
            "recipients": s.recipients,
        }
        for s in schedules
    ]
