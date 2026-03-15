"""Activity / audit log router."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.activity_log import ActivityLog
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas import ActivityLogOut

router = APIRouter(prefix="/api/activity-logs", tags=["Activity Logs"])

ADMIN_ROLES = ("admin", "manager", "store_manager")


@router.get("", response_model=dict)
def list_activity_logs(
    user_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ADMIN_ROLES:
        raise HTTPException(403, "Admin or manager role required to view activity logs")

    q = db.query(ActivityLog)
    if user_id is not None:
        q = q.filter(ActivityLog.user_id == user_id)
    if module:
        q = q.filter(ActivityLog.module == module)
    if action:
        q = q.filter(ActivityLog.action.ilike(f"%{action}%"))
    if status:
        q = q.filter(ActivityLog.status == status)
    if start_date:
        q = q.filter(ActivityLog.timestamp >= start_date)
    if end_date:
        q = q.filter(ActivityLog.timestamp <= end_date)

    total = q.count()
    pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = q.order_by(ActivityLog.timestamp.desc()).offset(offset).limit(page_size).all()

    return {
        "items": [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "user_id": log.user_id,
                "username": log.username,
                "action": log.action,
                "module": log.module,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "status": log.status,
                "error_message": log.error_message,
            }
            for log in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
