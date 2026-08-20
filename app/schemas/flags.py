import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.flags import FlagStatus


class FlagBase(BaseModel):
    flag_type: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1)
    status: FlagStatus | None = None
    resolved_at: datetime | None = None


class FlagCreate(FlagBase):
    pass


class FlagUpdate(BaseModel):
    flag_type: str | None = Field(default=None, min_length=1, max_length=100)
    reason: str | None = Field(default=None, min_length=1)
    status: FlagStatus | None = None
    resolved_at: datetime | None = None


class FlagRead(FlagBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    bill_id: uuid.UUID
    status: FlagStatus
    created_at: datetime
    updated_at: datetime
