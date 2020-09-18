from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    status,
    HTTPException,
)

from CTFe.config.database import dal
from CTFe.models import (
    Attempt,
    Team,
    Challenge,
)
from CTFe.schemas import attempt_schemas
from CTFe.operations import (
    attempt_ops,
    team_ops,
    challenge_ops,
)


router = APIRouter()


@router.post("/", response_model=attempt_schemas.AttemptDetails)
async def create_attempt(
    *,
    attempt_create: attempt_schemas.AttemptCreate,
    session: Session = Depends(dal.get_session),
) -> attempt_schemas.AttemptDetails:
    """ Create new attempt DB record """

    # Check if team record exists
    conditions_team = and_(
        Team.id == attempt_create.team_id,
    )

    if team_ops.read_teams_by_(session, conditions_team).first() is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Check if challenge record exists
    conditions_challenge = and_(
        Challenge.id == attempt_create.challenge_id,
    )

    if challenge_ops.read_challenges_by_(session, conditions_challenge).first() is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    db_attempt = attempt_ops.create_attempt(session, attempt_create)

    return db_attempt


@router.get("/{id}", response_model=attempt_schemas.AttemptDetails)
async def get_attempt(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> attempt_schemas.AttemptDetails:
    """ Retrieve a attempt record from DB """
    conditions = and_(
        Attempt.id == id,
    )

    db_attempt = attempt_ops.read_attempts_by_(session, conditions).first()

    if db_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )

    return db_attempt


@router.get("/", response_model=List[attempt_schemas.AttemptDetails])
async def get_all_attempts(
    session: Session = Depends(dal.get_session)
) -> List[attempt_schemas.AttemptDetails]:
    """ Retreive multiple attempt records from DB """
    db_attempts = attempt_ops.read_attempts_by_(session, and_())
    return db_attempts.all()


@router.put("/{id}", response_model=attempt_schemas.AttemptDetails)
async def update_attempt(
    *,
    id: int,
    attempt_update: attempt_schemas.AttemptUpdate,
    session: Session = Depends(dal.get_session)
) -> attempt_schemas.AttemptDetails:
    """ Update a attempt record from DB """
    conditions = and_(
        Attempt.id == id,
    )

    db_attempt = attempt_ops.read_attempts_by_(
        session, conditions).first()

    if db_attempt is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )

    db_attempt = attempt_ops.update_attempt(
        session, db_attempt, attempt_update)
    return db_attempt


@router.delete("/{id}", status_code=204)
def delete_attempt(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete a attempt record from DB """
    conditions = and_(
        Attempt.id == id,
    )

    db_attempt = attempt_ops.read_attempts_by_(
        session, conditions).first()

    if db_attempt is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Attempt not found"
        )

    attempt_ops.delete_attempt(session, db_attempt)
