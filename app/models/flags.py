import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.bills import Bill
    from app.models.users import User


def _enum_values(enum_cls: type[enum.StrEnum]) -> list[str]:
    """Make SQLAlchemy store an enum's lowercase `.value` in Postgres, not its `.name`."""
    return [member.value for member in enum_cls]


class FlagStatus(enum.StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Flag(Base):
    __tablename__ = "flags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bills.id"), nullable=False, index=True)
    # `flag_type` is left as a free-text field per the ERD (unlike `status`, it isn't marked
    # `enum`), so it's not mapped to a Python Enum.
    flag_type: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[FlagStatus] = mapped_column(
        SAEnum(FlagStatus, name="flag_status", values_callable=_enum_values),
        default=FlagStatus.OPEN,
        server_default=FlagStatus.OPEN.value,
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship()
    bill: Mapped["Bill"] = relationship(back_populates="flags")
