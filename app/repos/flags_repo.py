import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flags import Flag


async def list_by_bill(db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID) -> list[Flag]:
    result = await db.execute(select(Flag).where(Flag.user_id == user_id, Flag.bill_id == bill_id))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, user_id: uuid.UUID, flag_id: uuid.UUID) -> Flag | None:
    result = await db.execute(select(Flag).where(Flag.user_id == user_id, Flag.id == flag_id))
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    user_id: uuid.UUID,
    bill_id: uuid.UUID,
    flag_type: str,
    reason: str,
    **fields: Any,
) -> Flag:
    flag = Flag(user_id=user_id, bill_id=bill_id, flag_type=flag_type, reason=reason, **fields)
    db.add(flag)
    await db.flush()
    await db.refresh(flag)
    return flag


async def update(
    db: AsyncSession, user_id: uuid.UUID, flag_id: uuid.UUID, **fields: Any
) -> Flag | None:
    flag = await get_by_id(db, user_id, flag_id)
    if flag is None:
        return None
    for key, value in fields.items():
        setattr(flag, key, value)
    await db.flush()
    await db.refresh(flag)
    return flag


async def delete(db: AsyncSession, user_id: uuid.UUID, flag_id: uuid.UUID) -> bool:
    flag = await get_by_id(db, user_id, flag_id)
    if flag is None:
        return False
    await db.delete(flag)
    await db.flush()
    return True
