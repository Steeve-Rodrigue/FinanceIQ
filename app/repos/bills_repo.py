import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bills import Bill


async def list_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[Bill]:
    result = await db.execute(select(Bill).where(Bill.user_id == user_id))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID) -> Bill | None:
    result = await db.execute(select(Bill).where(Bill.user_id == user_id, Bill.id == bill_id))
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    storage_key: str,
    file_hash: str,
    **fields: Any,
) -> Bill:
    bill = Bill(user_id=user_id, name=name, storage_key=storage_key, file_hash=file_hash, **fields)
    db.add(bill)
    await db.flush()
    await db.refresh(bill)
    return bill


async def update(
    db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID, **fields: Any
) -> Bill | None:
    bill = await get_by_id(db, user_id, bill_id)
    if bill is None:
        return None
    for key, value in fields.items():
        setattr(bill, key, value)
    await db.flush()
    await db.refresh(bill)
    return bill


async def delete(db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Bill)
        .where(Bill.user_id == user_id, Bill.id == bill_id)
        .options(
            selectinload(Bill.line_items),
            selectinload(Bill.flags),
            selectinload(Bill.elicitations),
        )
    )
    bill = result.scalar_one_or_none()
    if bill is None:
        return False
    await db.delete(bill)
    await db.flush()
    return True
