import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.flags import Flag
from app.repos import bills_repo, flags_repo

# CRUD baseline only. Deciding *when* to raise a flag is part of the confidence/retry/
# elicitation decision loop in /CLAUDE.md (auditor agent, low-confidence branches, etc.) and is
# out of scope here - this module only stores and retrieves flags a caller already decided to
# create.


async def list_flags(db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID) -> list[Flag]:
    return await flags_repo.list_by_bill(db, user_id, bill_id)


async def get_flag(
    db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID, flag_id: uuid.UUID
) -> Flag:
    flag = await flags_repo.get_by_id(db, user_id, flag_id)
    if flag is None or flag.bill_id != bill_id:
        raise NotFoundError(f"flag {flag_id} not found")
    return flag


async def create_flag(
    db: AsyncSession,
    user_id: uuid.UUID,
    bill_id: uuid.UUID,
    flag_type: str,
    reason: str,
    **fields: Any,
) -> Flag:
    bill = await bills_repo.get_by_id(db, user_id, bill_id)
    if bill is None:
        raise NotFoundError(f"bill {bill_id} not found")
    flag = await flags_repo.create(
        db, user_id, bill_id, flag_type=flag_type, reason=reason, **fields
    )
    await db.commit()
    return flag


async def update_flag(
    db: AsyncSession,
    user_id: uuid.UUID,
    bill_id: uuid.UUID,
    flag_id: uuid.UUID,
    **fields: Any,
) -> Flag:
    await get_flag(db, user_id, bill_id, flag_id)
    flag = await flags_repo.update(db, user_id, flag_id, **fields)
    if flag is None:
        raise NotFoundError(f"flag {flag_id} not found")
    await db.commit()
    return flag


async def delete_flag(
    db: AsyncSession, user_id: uuid.UUID, bill_id: uuid.UUID, flag_id: uuid.UUID
) -> None:
    await get_flag(db, user_id, bill_id, flag_id)
    deleted = await flags_repo.delete(db, user_id, flag_id)
    if not deleted:
        raise NotFoundError(f"flag {flag_id} not found")
    await db.commit()
