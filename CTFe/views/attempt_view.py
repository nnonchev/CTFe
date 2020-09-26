from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from CTFe.config.database import dal
from CTFe.operations import (
    attempt_ops,
    team_ops,
    challenge_ops,
)
from CTFe.models import (
    Attempt,
    Team,
    Challenge,
)
from CTFe.schemas import attempt_schemas


router = APIRouter()


@router.post("/", response_model=attempt_schemas.Details)
async def create_attempt(
    *,
    attempt_create: attempt_schemas.Create,
    session: Session = Depends(dal.get_session),
) -> attempt_schemas.Details:
    """ Create new attempt DB record """

    conditions = and_(
        Team.id == attempt_create.team_id,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    conditions = and_(
        Challenge.id == attempt_create.challenge_id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if not db_challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    db_attempt = attempt_ops.create_attempt(session, attempt_create)

    return db_attempt


@router.get("/{id}", response_model=attempt_schemas.Details)
async def get_attempt(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> attempt_schemas.Details:
    """ Get attempt record from DB """

    conditions = and_(
        Attempt.id == id,
    )

    db_attempt = attempt_ops.query_attempts_by_(session, conditions).first()

    if db_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    return db_attempt


@router.get("/", response_model=List[attempt_schemas.Details])
async def get_all_attempts(
    *,
    session: Session = Depends(dal.get_session)
) -> List[attempt_schemas.Details]:
    """ Get all attempt records from DB """

    db_attempts = attempt_ops.query_attempts_by_(session).all()

    return db_attempts


@router.delete("/{id}", status_code=204)
async def delete_attempt(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete attempt record from DB """

    conditions = and_(
        Attempt.id == id,
    )

    db_attempt = attempt_ops.query_attempts_by_(session, conditions).first()

    if db_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )

    attempt_ops.delete_attempt(session, db_attempt)
