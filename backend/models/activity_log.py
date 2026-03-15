"""System-wide audit trail."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_timestamp", "timestamp"),
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_module", "module"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    username: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))  # CREATE_INVOICE, VOID_TRANSACTION, etc.
    module: Mapped[str] = mapped_column(String(30))   # store, financial, auth, inventory, etc.
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    before_state: Mapped[Optional[str]] = mapped_column(Text)  # JSON
    after_state: Mapped[Optional[str]] = mapped_column(Text)   # JSON
    status: Mapped[str] = mapped_column(String(20), default="success")  # success|failure
    error_message: Mapped[Optional[str]] = mapped_column(Text)
