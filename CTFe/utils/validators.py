from fastapi import (
    Depends,
    HTTPException,
    status,
)

from CTFe.models import User
from CTFe.operations import auth_ops
from CTFe.utils import enums


def _validate_user_type(
    user_type: str,
    db_user: User = Depends(auth_ops.get_current_user),
):
    if not enums.UserType.has_type(user_type):
        raise ValueError("Wrong user type")

    if db_user.user_type != enums.UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have the correct access"
        )


def validate_admin(): return (
    _validate_user_type(enums.UserType.ADMIN)
)


def validate_player(): return (
    _validate_user_type(enums.UserType.PLAYER)
)


def validate_contributor(): return (
    _validate_user_type(enums.UserType.CONTRIBUTOR)
)
