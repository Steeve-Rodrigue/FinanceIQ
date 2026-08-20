import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill_line_items import BillLineItem


async def list_by_bill(
    db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID
) -> list[BillLineItem]:
    result = await db.execute(
        select(BillLineItem).where(BillLineItem.user_id == user_id, BillLineItem.bill_id == bill_id)
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, user_id: uuid.UUID, line_item_id: uuid.UUID
) -> BillLineItem | None:
    result = await db.execute(
        select(BillLineItem).where(BillLineItem.user_id == user_id, BillLineItem.id == line_item_id)
    )
    return result.scalar_one_or_none()


async def create(
    db: AsyncSession,
    user_id: uuid.UUID,
    bill_id: uuid.UUID,
    description: str,
    line_total: float,
    **fields: Any,
) -> BillLineItem:
    line_item = BillLineItem(
        user_id=user_id,
        bill_id=bill_id,
        description=description,
        line_total=line_total,
        **fields,
    )
    db.add(line_item)
    await db.flush()
    await db.refresh(line_item)
    return line_item


async def update(
    db: AsyncSession, user_id: uuid.UUID, line_item_id: uuid.UUID, **fields: Any
) -> BillLineItem | None:
    line_item = await get_by_id(db, user_id, line_item_id)
    if line_item is None:
        return None
    for key, value in fields.items():
        setattr(line_item, key, value)
    await db.flush()
    await db.refresh(line_item)
    return line_item


async def delete(db: AsyncSession, user_id: uuid.UUID, line_item_id: uuid.UUID) -> bool:
    line_item = await get_by_id(db, user_id, line_item_id)
    if line_item is None:
        return False
    await db.delete(line_item)
    await db.flush()
    return True
