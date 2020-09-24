from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
)

from CTFe.config.database import dal
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.operations import (
    auth_ops,
    user_ops,
)
from CTFe.utils import pwd_utils


router = APIRouter()


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(dal.get_session),
):
    conditions = and_(
        User.username == form_data.username,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if (
        (db_user is None) or
        (not pwd_utils.verify_password(form_data.password, db_user.password))
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    token = auth_ops.create_access_token(id=db_user.id)

    return {
        "token": token,
        "token_type": "bearer",
    }


@router.post("/register")
async def register(
    *,
    user_create: user_schemas.UserCreate,
    session: Session = Depends(dal.get_session),
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

    token = auth_ops.create_access_token(id=db_user.id)

    return {
        "token": token,
        "token_type": "bearer",
    }


@router.post(
    "/logout",
    status_code=204,
)
async def logout_user(
    token: str = Depends(auth_ops.oauth2_scheme),
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in",
        )


@router.get(
    "/me",
    response_model=user_schemas.UserDetails,
)
def auth_test(
    db_user: User = Depends(auth_ops.get_current_user),
) -> User:
    return db_user
