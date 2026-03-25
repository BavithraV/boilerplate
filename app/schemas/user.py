"""User-facing schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    full_name: str | None
    created_at: datetime
