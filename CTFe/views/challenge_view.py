from uuid import uuid4
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    BackgroundTasks,
)

from CTFe.config.database import dal
from CTFe.operations import challenge_ops
from CTFe.models import Challenge
from CTFe.schemas import challenge_schemas


router = APIRouter()


@router.post("/", response_model=challenge_schemas.Details)
async def create_challenge(
    *,
    challenge_create: challenge_schemas.Create,
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.Details:
    """ Create new challenge DB record """

    # Make sure unique fields are not already used
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

    db_challenge = challenge_ops.create_challenge(session, challenge_create)

    return db_challenge


@router.get("/{id}", response_model=challenge_schemas.Details)
async def get_challenge(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> challenge_schemas.Details:
    """ Get challenge record from DB """

    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    return db_challenge


@router.get("/name/{name}", response_model=challenge_schemas.Details)
async def get_challenge_by_name(
    *,
    name: str,
    session: Session = Depends(dal.get_session)
) -> challenge_schemas.Details:
    """ Get challenge record from DB """

    conditions = and_(
        Challenge.name == name,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    return db_challenge


@router.get("/", response_model=List[challenge_schemas.Details])
async def get_all_challenges(
    *,
    session: Session = Depends(dal.get_session)
) -> List[challenge_schemas.Details]:
    """ Get all challenge records from DB """

    db_challenges = challenge_ops.query_challenges_by_(session).all()

    return db_challenges


@router.put("/{id}", response_model=challenge_schemas.Details)
async def update_challenge(
    *,
    id: int,
    challenge_update: challenge_schemas.Update,
    session: Session = Depends(dal.get_session)
) -> challenge_schemas.Details:
    """ Update challenge record from DB """

    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    db_challenge = challenge_ops.update_challenge(
        session, db_challenge, challenge_update)

    return db_challenge


@router.delete("/{id}", status_code=204)
async def delete_challenge(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete challenge record from DB """

    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    challenge_ops.delete_challenge(session, db_challenge)


@router.post("/{id}/upload-file", response_model=challenge_schemas.Details)
def upload_file(
    *,
    id: int,
    challenge_file: UploadFile = File(...),
    background_task: BackgroundTasks,
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.Details:
    """ Upload file associated with a challenge record """

    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    if db_challenge.file_name is not None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="There is already a file associated with this challenge"
        )

    filename = uuid4().hex + f"_{ challenge_file.filename }"
    background_task.add_task(challenge_ops.store_file,
                             filename, challenge_file)

    challenge_update = challenge_schemas.Update(file_name=filename)
    db_challenge = challenge_ops.update_challenge(
        session, db_challenge, challenge_update)

    return db_challenge


@router.post("/{id}/remove-file", response_model=challenge_schemas.Details)
def remove_file(
    *,
    id: int,
    background_task: BackgroundTasks,
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.Details:
    """ Remove uploaded file associated with a challenge record """

    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.query_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    if db_challenge.file_name is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="There is no file associated with this challenge"
        )

    filename = db_challenge.file_name
    background_task.add_task(challenge_ops.remove_file, filename)

    challenge_update = challenge_schemas.Update(file_name=None)
    db_challenge = challenge_ops.update_challenge(
        session, db_challenge, challenge_update)

    return db_challenge
