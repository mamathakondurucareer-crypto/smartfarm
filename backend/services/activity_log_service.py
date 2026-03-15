"""Activity log service — write audit entries from any router."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    action: str,
    module: str,
    username: str = "system",
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    description: str = "",
    before: Optional[str] = None,
    after: Optional[str] = None,
    ip: Optional[str] = None,
    status: str = "success",
    error: Optional[str] = None,
) -> None:
    """Add an audit log entry.  Caller controls the transaction — do NOT commit here."""
    log = ActivityLog(
        timestamp=datetime.now(timezone.utc),
        user_id=user_id,
        username=username,
        action=action,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip,
        before_state=before,
        after_state=after,
        status=status,
        error_message=error,
    )
    db.add(log)
    # do NOT commit here — caller controls the transaction
