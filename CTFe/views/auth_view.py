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

    db_user = user_ops.read_user_by_(session, conditions)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

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
