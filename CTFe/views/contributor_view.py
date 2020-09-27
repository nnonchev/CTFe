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
)
from CTFe.models import User
from CTFe.schemas import contributor_schemas


router = APIRouter()


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
