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
    contributor_ops,
    auth_ops,
    challenge_ops,
)
from CTFe.models import (
    User,
    Challenge,
)
from CTFe.schemas import (
    contributor_schemas,
    challenge_schemas,
)


router = APIRouter()


@router.get("/list-challenges", response_model=List[challenge_schemas.Details])
def list_challenges(
    *,
    db_contributor: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.Details:
    """ List all challenges created by the current contributor """

    conditions = and_(
        Challenge.owner_id == db_contributor.id,
    )

    db_challenges = challenge_ops.query_challenges_by_(
        session, conditions).all()

    return db_challenges


@router.get("/username/{username}", response_model=contributor_schemas.Details)
async def get_contributor_by_username(
    *,
    username: str,
    session: Session = Depends(dal.get_session)
) -> contributor_schemas.Details:
    """ Get contributor record from DB """

    conditions = and_(
        User.username == username,
    )

    db_contributor = contributor_ops.query_contributors_by_(
        session, conditions).first()

    if db_contributor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor not found",
        )

    return db_contributor


@router.get("/{id}", response_model=contributor_schemas.Details)
async def get_contributor(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> contributor_schemas.Details:
    """ Get contributor record from DB """

    conditions = and_(
        User.id == id,
    )

    db_contributor = contributor_ops.query_contributors_by_(
        session, conditions).first()

    if db_contributor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor not found",
        )

    return db_contributor


@router.get("/", response_model=List[contributor_schemas.Details])
async def get_all_contributors(
    *,
    session: Session = Depends(dal.get_session)
) -> List[contributor_schemas.Details]:
    """ Get all contributor records from DB """

    db_contributors = contributor_ops.query_contributors_by_(session).all()

    return db_contributors


@router.put("/", response_model=contributor_schemas.Details)
async def update_contributor(
    *,
    contributor_update: contributor_schemas.Update,
    db_contributor: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session)
) -> contributor_schemas.Details:
    """ Update contributor record from DB """

    db_contributor = contributor_ops.update_contributor(
        session, db_contributor, contributor_update)

    return db_contributor


@router.delete("/", status_code=204)
async def delete_contributor(
    *,
    db_contributor: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session)
):
    """ Delete contributor record from DB """

    contributor_ops.delete_contributor(session, db_contributor)


@router.post("/create-challenge", response_model=contributor_schemas.Details)
def create_challenge(
    *,
    challenge_create: challenge_schemas.Create,
    db_contributor: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> contributor_schemas.Details:
    """ Create challenge and assign this contributor to it """

    from CTFe.operations import challenge_ops

    # Challenge name is already taken
    conditions = and_(
        Challenge.name == challenge_create.name,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The name: { challenge_create.name } is already taken",
        )

    contributor_ops.create_challenge(
        session, challenge_create, db_contributor)

    return db_contributor


@router.put("/update-challenge/{challenge_id}", response_model=contributor_schemas.Details)
def update_challenge(
    *,
    challenge_id: int,
    challenge_update: challenge_schemas.Update,
    db_contributor: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> contributor_schemas.Details:
    """ Update contributor's challenge """

    conditions = and_(
        Challenge.id == challenge_id,
        Challenge.owner_id == db_contributor.id,
    )

    db_challenge = challenge_ops.query_challenges_by_(session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
        
    challenge_ops.update_challenge(session, db_challenge, challenge_update)

    return db_contributor


@router.post("/remove-challenge/{challenge_id}", response_model=contributor_schemas.Details)
def remove_challenge(
    *,
    challenge_id: int,
    db_contributor: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> contributor_schemas.Details:
    """ Delete a challenge related to this contributor """

    conditions = and_(
        Challenge.id == challenge_id,
        Challenge.owner_id == db_contributor.id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    challenge_ops.delete_challenge(session, db_challenge)

    return db_contributor
