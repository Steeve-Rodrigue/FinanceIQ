import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import NotFoundError
from app.models.users import User
from app.schemas.flags import FlagCreate, FlagRead, FlagUpdate
from app.services import flags_service

router = APIRouter(prefix="/bills/{bill_id}/flags", tags=["flags"])

# CRUD baseline only - see app/services/flags_service.py for why the decision-loop logic that
# decides *when* to raise a flag is intentionally absent from this router.


@router.post("/", response_model=FlagRead, status_code=status.HTTP_201_CREATED)
async def create_flag(
    bill_id: uuid.UUID,
    body: FlagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlagRead:
    fields = body.model_dump(exclude={"flag_type", "reason"}, exclude_unset=True)
    try:
        flag = await flags_service.create_flag(
            db, current_user.id, bill_id, flag_type=body.flag_type, reason=body.reason, **fields
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FlagRead.model_validate(flag)


@router.get("/", response_model=list[FlagRead])
async def list_flags(
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FlagRead]:
    flags = await flags_service.list_flags(db, current_user.id, bill_id)
    return [FlagRead.model_validate(flag) for flag in flags]


@router.get("/{flag_id}", response_model=FlagRead)
async def get_flag(
    bill_id: uuid.UUID,
    flag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlagRead:
    try:
        flag = await flags_service.get_flag(db, current_user.id, bill_id, flag_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FlagRead.model_validate(flag)


@router.patch("/{flag_id}", response_model=FlagRead)
async def update_flag(
    bill_id: uuid.UUID,
    flag_id: uuid.UUID,
    body: FlagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlagRead:
    fields = body.model_dump(exclude_unset=True)
    try:
        flag = await flags_service.update_flag(db, current_user.id, bill_id, flag_id, **fields)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FlagRead.model_validate(flag)


@router.delete("/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flag(
    bill_id: uuid.UUID,
    flag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await flags_service.delete_flag(db, current_user.id, bill_id, flag_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
