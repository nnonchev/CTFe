from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
)

from CTFe.config.database import dal
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.operations import user_ops


router = APIRouter()


@router.post(
    "/login",
    response_model=user_schemas.UserDetails,
)
async def login_player(
    *,
    user_login: user_schemas.UserLogin,
    session: Session = Depends(dal.get_session),
):
    conditions = and_(
        User.username == user_login.username,
        User.password == user_login.password,
    )

    db_user = user_ops.read_user_by_(session, conditions)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user
