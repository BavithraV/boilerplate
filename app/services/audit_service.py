"""Audit logging service."""

import logging

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Persist audit events to PostgreSQL."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def log_action(
        self,
        user_id: int | None,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict | None = None,
    ) -> None:
        """Write an audit event."""
        event = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
        self.db.add(event)
        self.db.commit()
        logger.info(
            "Audit event created",
            extra={
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
            },
        )
