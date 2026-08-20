import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.exceptions import NotFoundError
from app.models.users import User
from app.schemas.elicitations import ElicitationCreate, ElicitationRead, ElicitationUpdate
from app.services import elicitations_service

router = APIRouter(prefix="/bills/{bill_id}/elicitations", tags=["elicitations"])

# CRUD baseline only - see app/services/elicitations_service.py for why the actual
# pause/resume elicitation flow (MCP server, clarify.html, resuming a paused agent) is
# intentionally absent from this router.


@router.post("/", response_model=ElicitationRead, status_code=status.HTTP_201_CREATED)
async def create_elicitation(
    bill_id: uuid.UUID,
    body: ElicitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ElicitationRead:
    fields = body.model_dump(exclude={"stage", "question"}, exclude_unset=True)
    try:
        elicitation = await elicitations_service.create_elicitation(
            db, current_user.id, bill_id, stage=body.stage, question=body.question, **fields
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ElicitationRead.model_validate(elicitation)


@router.get("/", response_model=list[ElicitationRead])
async def list_elicitations(
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ElicitationRead]:
    elicitations = await elicitations_service.list_elicitations(db, current_user.id, bill_id)
    return [ElicitationRead.model_validate(elicitation) for elicitation in elicitations]


@router.get("/{elicitation_id}", response_model=ElicitationRead)
async def get_elicitation(
    bill_id: uuid.UUID,
    elicitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ElicitationRead:
    try:
        elicitation = await elicitations_service.get_elicitation(
            db, current_user.id, bill_id, elicitation_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ElicitationRead.model_validate(elicitation)


@router.patch("/{elicitation_id}", response_model=ElicitationRead)
async def update_elicitation(
    bill_id: uuid.UUID,
    elicitation_id: uuid.UUID,
    body: ElicitationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ElicitationRead:
    fields = body.model_dump(exclude_unset=True)
    try:
        elicitation = await elicitations_service.update_elicitation(
            db, current_user.id, bill_id, elicitation_id, **fields
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ElicitationRead.model_validate(elicitation)


@router.delete("/{elicitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_elicitation(
    bill_id: uuid.UUID,
    elicitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await elicitations_service.delete_elicitation(db, current_user.id, bill_id, elicitation_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
