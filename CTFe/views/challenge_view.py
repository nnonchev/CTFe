from uuid import uuid4
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    status,
    HTTPException,
    File,
    UploadFile,
    BackgroundTasks,
)

from CTFe.config.database import dal
from CTFe.models import (
    Challenge,
    User,
)
from CTFe.schemas import challenge_schemas
from CTFe.operations import (
    challenge_ops,
    auth_ops,
)
from CTFe.utils import (
    enums,
)


router = APIRouter()


@router.post("/", response_model=challenge_schemas.ChallengeDetails)
async def create_challenge(
    *,
    challenge_create: challenge_schemas.ChallengeCreate,
    db_user: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.ChallengeDetails:
    """ Create new challenge DB record """
    conditions = and_(
        Challenge.name == challenge_create.name,
    )

    # Check if the current user is a contributor
    if db_user.user_type != enums.UserType.CONTRIBUTOR:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Only contributors can create challenges"
        )

    # Check if a challenge record with the same unique fields already exists
    if challenge_ops.read_challenges_by_(session, conditions).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The name: { challenge_create.name } is already taken"
        )

    db_challenge = challenge_ops.create_challenge(session, challenge_create, db_user)

    return db_challenge


@router.get("/{id}", response_model=challenge_schemas.ChallengeDetails)
async def get_challenge(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> challenge_schemas.ChallengeDetails:
    """ Retrieve a challenge record from DB """
    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.read_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    return db_challenge


@router.get("/name/{name}", response_model=challenge_schemas.ChallengeDetails)
async def get_challenge_by_name(
    *,
    name: str,
    session: Session = Depends(dal.get_session)
) -> challenge_schemas.ChallengeDetails:
    """ Retrieve a challenge record from DB """
    conditions = and_(
        Challenge.name == name,
    )

    db_challenge = challenge_ops.read_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    return db_challenge


@router.get("/", response_model=List[challenge_schemas.ChallengeDetails])
async def get_all_challenges(
    session: Session = Depends(dal.get_session)
) -> List[challenge_schemas.ChallengeDetails]:
    """ Retreive multiple challenge records from DB """
    db_challenges = challenge_ops.read_challenges_by_(session, and_())
    return db_challenges.all()


@router.put("/{id}", response_model=challenge_schemas.ChallengeDetails)
async def update_challenge(
    *,
    id: int,
    challenge_update: challenge_schemas.ChallengeUpdate,
    db_user: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session)
) -> challenge_schemas.ChallengeDetails:
    """ Update a challenge record from DB """
    
    # Check if the current user is a contributor
    if db_user.user_type != enums.UserType.CONTRIBUTOR:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Only contributors can create challenges"
        )

    conditions = and_(
        Challenge.id == id,
        Challenge.owner_id == db_user.id,
    )

    db_challenge = challenge_ops.read_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    db_challenge = challenge_ops.update_challenge(
        session, db_challenge, challenge_update)
    return db_challenge


@router.post("/{id}/upload-file", response_model=challenge_schemas.ChallengeDetails)
def upload_file(
    *,
    id: int,
    challenge_file: UploadFile = File(...),
    background_task: BackgroundTasks,
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.ChallengeDetails:
    """ Upload file associated to a challenge record """
    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.read_challenges_by_(
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

    challenge_update = challenge_schemas.ChallengeUpdate(file_name=filename)
    db_challenge = challenge_ops.update_challenge(
        session, db_challenge, challenge_update)

    return db_challenge


@router.post("/{id}/remove-file", response_model=challenge_schemas.ChallengeDetails)
def upload_file(
    *,
    id: int,
    background_task: BackgroundTasks,
    session: Session = Depends(dal.get_session),
) -> challenge_schemas.ChallengeDetails:
    """ Remove uploaded file associated to a challenge record """
    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.read_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    if db_challenge.file_name is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="There is no file for this challenge"
        )        

    filename = db_challenge.file_name
    background_task.add_task(challenge_ops.remove_file, filename)

    challenge_update = challenge_schemas.ChallengeUpdate(file_name=None)
    db_challenge = challenge_ops.update_challenge(
        session, db_challenge, challenge_update)

    return db_challenge


@router.delete("/{id}", status_code=204)
def delete_challenge(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete a challenge record from DB """
    conditions = and_(
        Challenge.id == id,
    )

    db_challenge = challenge_ops.read_challenges_by_(
        session, conditions).first()

    if db_challenge is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )

    challenge_ops.delete_challenge(session, db_challenge)
