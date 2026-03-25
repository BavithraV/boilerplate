"""User model."""

from datetime import datetime

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.db.base import Base
from app.models.associations import user_roles
from app.models.role import Role


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")

    @classmethod
    def get_or_create_from_token(
        cls,
        db: Session,
        token_payload: dict,
    ) -> "User":
        """Find or create a user from an Entra ID token payload."""
        external_id = token_payload.get("sub")
        email = (
            token_payload.get("preferred_username")
            or token_payload.get("upn")
            or f"{external_id}@unknown.local"
        )
        full_name = token_payload.get("name")
        roles_from_token = token_payload.get("roles", [])

        existing_user = db.scalar(select(cls).where(cls.external_id == external_id))
        if existing_user:
            return existing_user

        user = cls(
            email=email,
            full_name=full_name,
            external_id=external_id,
        )
        if roles_from_token:
            role_records = []
            for role_name in roles_from_token:
                role = db.scalar(select(Role).where(Role.name == role_name))
                if role is None:
                    role = Role(
                        name=role_name, description=f"Imported role {role_name}"
                    )
                    db.add(role)
                    db.flush()
                role_records.append(role)
            user.roles = role_records

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
