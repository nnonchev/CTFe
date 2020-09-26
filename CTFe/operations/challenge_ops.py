import os
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import (
    Session,
    Query,
)
from sqlalchemy.sql.expression import BooleanClauseList
from fastapi import UploadFile

from CTFe.operations.CRUD_ops import (
    create_record,
    query_records,
    update_record,
    delete_record,
)
from CTFe.models import Challenge
from CTFe.schemas import challenge_schemas
from CTFe.config import constants


def create_challenge(
    session: Session,
    challenge_create: challenge_schemas.Create,
) -> Challenge:
    """ Create challenge record """

    db_challenge = create_record(session, Challenge, challenge_create)

    return db_challenge


def query_challenges_by_(
    session: Session,
    conditions: Optional[BooleanClauseList] = and_(),
) -> Query:
    """ Query challenge records """

    query_challenges = query_records(session, Challenge, conditions)

    return query_challenges


def update_challenge(
    session: Session,
    db_challenge: Challenge,
    challenge_update: challenge_schemas.Update,
) -> Challenge:
    """ Update challenge record """

    db_challenge = update_record(session, db_challenge, challenge_update)

    return db_challenge


def store_file(
    filename: str,
    upload_file: UploadFile,
):
    upload_file_loc = os.path.join(
        constants.UPLOAD_FILE_LOCATION,
        filename
    )

    with open(upload_file_loc, "wb") as buffer:
        for chunk in iter(
            lambda: upload_file.file.read(constants.UPLOAD_FILE_SIZE), b''
        ):
            buffer.write(chunk)


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
    """ Delete challenge record """

    delete_record(session, db_challenge)
