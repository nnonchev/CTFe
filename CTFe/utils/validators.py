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
from CTFe.utils import (
    enums,
    redis_utils,
)


class is_of_user_type:
    def __init__(
        self,
        user_type: enums.UserType,
    ):
        if not enums.UserType.has_type(user_type):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Wrong user_type value'
            )

        self.user_type = user_type

    async def __call__(
        self,
        token: Optional[str] = Cookie(None),
        session: Session = Depends(dal.get_session),
    ) -> bool:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not logged in",
            )

        user_payload = await redis_utils.retrieve_payload(token)

        conditions = and_(
            User.id == user_payload.id,
        )

        db_user = user_ops.read_user_by_(session, conditions)

        if db_user.user_type != self.user_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have the correct access"
            )
