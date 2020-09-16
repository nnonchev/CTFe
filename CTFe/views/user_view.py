from typing import Optional

from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    status,
    HTTPException,
)

from CTFe.config.database import dal
from CTFe.schemas import user_schemas
from CTFe.operations import user_ops


router = APIRouter()


@router.post("/", response_model=user_schemas.UserDetails)
def create_user(
    *,
    user_create: user_schemas.UserCreate,
    session: Session = Depends(dal.get_session),
) -> user_schemas.UserDetails:
    """ Create new user and save it into DB """
    db_user = user_ops.create_user(session, user_create)

    return db_user
