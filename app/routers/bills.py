import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import NotFoundError
from app.models.users import User
from app.schemas.bills import BillCreate, BillRead, BillUpdate
from app.services import bills_service

router = APIRouter(prefix="/bills", tags=["bills"])

# CRUD baseline only - see app/services/bills_service.py for why the decision-loop logic
# (confidence scoring, retry, elicitation) is intentionally absent from this router.


@router.post("/", response_model=BillRead, status_code=status.HTTP_201_CREATED)
async def create_bill(
    body: BillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillRead:
    fields = body.model_dump(exclude={"name", "storage_key", "file_hash"}, exclude_unset=True)
    try:
        bill = await bills_service.create_bill(
            db,
            current_user.id,
            name=body.name,
            storage_key=body.storage_key,
            file_hash=body.file_hash,
            **fields,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BillRead.model_validate(bill)


@router.get("/", response_model=list[BillRead])
async def list_bills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BillRead]:
    bills = await bills_service.list_bills(db, current_user.id)
    return [BillRead.model_validate(bill) for bill in bills]


@router.get("/{bill_id}", response_model=BillRead)
async def get_bill(
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillRead:
    try:
        bill = await bills_service.get_bill(db, current_user.id, bill_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BillRead.model_validate(bill)


@router.patch("/{bill_id}", response_model=BillRead)
async def update_bill(
    bill_id: uuid.UUID,
    body: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillRead:
    fields = body.model_dump(exclude_unset=True)
    try:
        bill = await bills_service.update_bill(db, current_user.id, bill_id, **fields)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BillRead.model_validate(bill)


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await bills_service.delete_bill(db, current_user.id, bill_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
