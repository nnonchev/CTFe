from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    Response,
    Cookie,
    status,
    HTTPException,
)

from CTFe.config.database import dal
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.operations import user_ops
from CTFe.utils import redis_utils
from CTFe.utils.redis_utils import redis_dal


router = APIRouter()


@router.get(
    "/me",
    response_model=user_schemas.UserDetails,
)
async def user_info(
    *,
    token: Optional[str] = Cookie(None),
    session: Session = Depends(dal.get_session),
) -> user_schemas.UserDetails:
    """ Get information on the currently logged in user """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in",
        )

    user_payload = await redis_utils.retrieve_payload(token, redis_dal)

    conditions = and_(
        User.id == user_payload.id,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user


@router.post(
    "/register",
    response_model=user_schemas.UserDetails,
)
async def register_user(
    *,
    user_create: user_schemas.UserCreate,
    session: Session = Depends(dal.get_session),
    response: Response,
):
    """ Check if user with username already exists """
    conditions = and_(
        User.username == user_create.username,
    )

    if user_ops.read_users_by_(session, conditions).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The username: { user_create.username } is already taken"
        )

    db_user = user_ops.create_user(session, user_create)

    user_payload = user_schemas.UserRedisPayload.from_orm(db_user)
    token = await redis_utils.store_payload(user_payload, redis_dal)

    response.set_cookie(key="token", value=token)

    return db_user


@router.post(
    "/login",
    response_model=user_schemas.UserDetails,
)
async def login_user(
    *,
    user_login: user_schemas.UserLogin,
    session: Session = Depends(dal.get_session),
    response: Response,
):
    conditions = and_(
        User.username == user_login.username,
        User.password == user_login.password,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_payload = user_schemas.UserRedisPayload.from_orm(db_user)
    token = await redis_utils.store_payload(user_payload, redis_dal)

    response.set_cookie(key="token", value=token)

    return db_user


@router.post(
    "/logout",
    status_code=204,
)
async def logout_user(
    *,
    token: Optional[str] = Cookie(None),
    response: Response,
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in",
        )

    user_payload = await redis_utils.retrieve_payload(token, redis_dal)
    await redis_utils.delete_key(user_payload.id, redis_dal)

    response.delete_cookie("token")
