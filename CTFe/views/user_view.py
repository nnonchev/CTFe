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
from CTFe.operations import user_ops
from CTFe.models import User
from CTFe.schemas import user_schemas


router = APIRouter()


@router.post("/", response_model=user_schemas.Details)
async def create_user(
    *,
    user_create: user_schemas.Create,
    session: Session = Depends(dal.get_session),
) -> user_schemas.Details:
    """ Create new user DB record """

    # Make sure unique fields are not already used
    conditions = and_(
        User.username == user_create.username,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The username: { user_create.username } is already taken",
        )

    db_user = user_ops.create_user(session, user_create)

    return db_user


@router.get("/{id}", response_model=user_schemas.Details)
async def get_user(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> user_schemas.Details:
    """ Get user record from DB """

    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return db_user


@router.get("/username/{username}", response_model=user_schemas.Details)
async def get_user_by_username(
    *,
    username: str,
    session: Session = Depends(dal.get_session)
) -> user_schemas.Details:
    """ Get user record from DB """

    conditions = and_(
        User.username == username,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return db_user


@router.get("/", response_model=List[user_schemas.Details])
async def get_all_users(
    *,
    session: Session = Depends(dal.get_session)
) -> List[user_schemas.Details]:
    """ Get all user records from DB """

    db_users = user_ops.query_users_by_(session).all()

    return db_users


@router.put("/{id}", response_model=user_schemas.Details)
async def update_user(
    *,
    id: int,
    user_update: user_schemas.Update,
    session: Session = Depends(dal.get_session)
) -> user_schemas.Details:
    """ Update user record from DB """

    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db_user = user_ops.update_user(session, db_user, user_update)

    return db_user


@router.delete("/{id}", status_code=204)
async def delete_user(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete user record from DB """

    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_ops.delete_user(session, db_user)
