from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    Depends,
    Cookie,
    status,
    HTTPException,
)

from CTFe.config.database import dal
from CTFe.operations import user_ops
from CTFe.models import User
from CTFe.utils.redis_utils import redis_dal
from CTFe.utils import (
    enums,
    redis_utils,
)


async def validate_admin(
    token: Optional[str] = Cookie(None),
    session: Session = Depends(dal.get_session),
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in",
        )

    user_payload = await redis_utils.retrieve_payload(token, redis_dal)

    conditions = and_(
        User.id == user_payload.id,
        User.user_type == enums.UserType.ADMIN,
    )

    db_user = user_ops.read_user_by_(session, conditions)

    if db_user.user_type is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have the correct access"
        )
