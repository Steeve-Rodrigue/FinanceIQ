import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.elicitations import Elicitation


async def list_by_bill(
    db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID
) -> list[Elicitation]:
    result = await db.execute(
        select(Elicitation).where(Elicitation.user_id == user_id, Elicitation.bill_id == bill_id)
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, user_id: uuid.UUID, elicitation_id: uuid.UUID
) -> Elicitation | None:
    result = await db.execute(
        select(Elicitation).where(Elicitation.user_id == user_id, Elicitation.id == elicitation_id)
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    user_id: uuid.UUID,
    bill_id: uuid.UUID,
    stage: Any,
    question: str,
    **fields: Any,
) -> Elicitation:
    elicitation = Elicitation(
        user_id=user_id, bill_id=bill_id, stage=stage, question=question, **fields
    )
    db.add(elicitation)
    await db.flush()
    await db.refresh(elicitation)
    return elicitation


async def update(
    db: AsyncSession, user_id: uuid.UUID, elicitation_id: uuid.UUID, **fields: Any
) -> Elicitation | None:
    elicitation = await get_by_id(db, user_id, elicitation_id)
    if elicitation is None:
        return None
    for key, value in fields.items():
        setattr(elicitation, key, value)
    await db.flush()
    await db.refresh(elicitation)
    return elicitation


async def delete(db: AsyncSession, user_id: uuid.UUID, elicitation_id: uuid.UUID) -> bool:
    elicitation = await get_by_id(db, user_id, elicitation_id)
    if elicitation is None:
        return False
    await db.delete(elicitation)
    await db.flush()
    return True
