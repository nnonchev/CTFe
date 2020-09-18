import os

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import (
    and_,
    BooleanClauseList,
)
from fastapi import UploadFile

from CTFe.models import Challenge
from CTFe.schemas import challenge_schemas
from CTFe.config import constants


def create_challenge(
    session: Session,
    challenge_create: challenge_schemas.ChallengeCreate,
) -> Challenge:
    """ Insert a challenge record in DB """
    db_challenge = Challenge(**challenge_create.dict())

    session.add(db_challenge)
    session.commit()
    session.refresh(db_challenge)

    return db_challenge


def read_challenges_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> Challenge:
    """ Query DB for a challenge based on multiple queries """
    return session.query(Challenge).filter(conditions)


def update_challenge(
    session: Session,
    db_challenge: Challenge,
    challenge_update: challenge_schemas.ChallengeUpdate,
) -> Challenge:
    """ Update challenge record in DB """

    # Cast to ChallengeUpdate pydantic model
    challenge_updated = (
        challenge_schemas.ChallengeUpdate.from_orm(db_challenge)
    )

    # Update the new fields
    challenge_data = challenge_updated.copy(
        update=challenge_update.dict(exclude_unset=True),
    )

    # Update fields
    (
        session
        .query(Challenge)
        .filter(Challenge.id == db_challenge.id)
        .update(challenge_data.dict())
    )

    session.commit()
    session.refresh(db_challenge)

    return db_challenge


def store_file(
    filename: str,
    upload_file: UploadFile,
):
    upload_file_loc = os.path.join(
        constants.UPLOAD_FILE_LOCATION,
        filename,
    )

    with open(upload_file_loc, "wb") as buffer:
        [
            buffer.write(chunk)
            for chunk in iter(
                lambda: upload_file.file.read(constants.UPLOAD_FILE_SIZE), b''
            )
        ]


def remove_file(
    filename: str
):
    filepath = os.path.join(
        constants.UPLOAD_FILE_LOCATION,
        filename
    )

    os.remove(filepath)


def delete_challenge(
    session: Session,
    db_challenge: Challenge,
):
    session.delete(db_challenge)
    session.commit()
