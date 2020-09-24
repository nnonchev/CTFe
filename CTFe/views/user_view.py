from typing import (
    List,
    Optional,
)

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
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.operations import user_ops
from CTFe.utils import enums


router = APIRouter()


@router.post("/", response_model=user_schemas.UserDetails)
async def create_user(
    *,
    user_create: user_schemas.UserCreate,
    session: Session = Depends(dal.get_session),
) -> user_schemas.UserDetails:
    """ Create new user DB record """
    conditions = and_(
        User.username == user_create.username,
    )

    # Check if a user record with the same unique fields already exists
    if user_ops.read_users_by_(session, conditions).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The username: { user_create.username } is already taken"
        )


    db_user = user_ops.create_user(session, user_create)

    return db_user


@router.get("/{id}", response_model=user_schemas.UserDetails)
async def get_user(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> user_schemas.UserDetails:
    """ Retrieve a user record from DB """
    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user


@router.get("/username/{username}", response_model=user_schemas.UserDetails)
async def get_user_by_username(
    *,
    username: str,
    session: Session = Depends(dal.get_session)
) -> user_schemas.UserDetails:
    """ Retrieve a user record from DB """
    conditions = and_(
        User.username == username,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user


@router.get("/", response_model=List[user_schemas.UserDetails])
async def get_all_users(
    session: Session = Depends(dal.get_session)
) -> List[user_schemas.UserDetails]:
    """ Retreive multiple users records from DB """
    db_users = user_ops.read_users_by_(session, and_())
    return db_users.all()


@router.put("/{id}", response_model=user_schemas.UserDetails)
async def update_user(
    *,
    id: int,
    user_update: user_schemas.UserUpdate,
    session: Session = Depends(dal.get_session)
) -> user_schemas.UserDetails:
    """ Update a user record from DB """
    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_user = user_ops.update_user(session, db_user, user_update)

    return db_user


@router.delete("/{id}", status_code=204)
def delete_user(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete a user record from DB """
    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    """ Delete user record from DB """
    user_ops.delete_user(session, db_user)
