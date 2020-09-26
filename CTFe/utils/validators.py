from fastapi import (
    Depends,
    HTTPException,
    status,
)

from CTFe.models import User
from CTFe.operations import auth_ops
from CTFe.utils import enums


class validate_user_type:
    def __init__(self, user_type: str):
        if not enums.UserType.has_type(user_type):
            raise ValueError("Wrong user type")

        self.user_type = user_type

    async def __call__(
        self,
        db_user: User = Depends(auth_ops.get_current_user),
    ):
        if db_user.user_type != self.user_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have the correct access"
            )
