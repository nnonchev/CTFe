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
    """ Verify user is registered and create JWT signed access token """

    incorrect_credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect username or password",
    )

    conditions = and_(
        User.username == form_data.username,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    is_correct_password = False

    try:
        is_correct_password = pwd_utils.verify_password(form_data.password, db_user.password)
    except ValueError:
        raise incorrect_credentials_exception
    except:
        raise

    if db_user is None:
        raise incorrect_credentials_exception
    elif not is_correct_password:
        raise incorrect_credentials_exception

    token = auth_ops.create_access_token(db_user=db_user)

    return {
        "token": token,
        "token_type": "bearer",
    }


@router.post("/register")
async def register(
    *,
    user_create: user_schemas.Create,
    session: Session = Depends(dal.get_session),
):
    """ Register user and return JWT signed access token """

    # Make sure username is not taken
    conditions = and_(
        User.username == user_create.username,
    )

    if user_ops.query_users_by_(session, conditions).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The username: { user_create.username } is already taken"
        )

    db_user = user_ops.create_user(session, user_create)

    token = auth_ops.create_access_token(db_user=db_user)

    return {
        "token": token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=204)
async def logout_user(
    token: str = Depends(auth_ops.oauth2_scheme),
):
    """ Logout user """

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in",
        )

    # TODO Remove token from redis


@router.get("/me", response_model=user_schemas.Details)
async def auth_test(
    db_user: User = Depends(auth_ops.get_current_user),
):
    """ Get user info """

    return db_user
