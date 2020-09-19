from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
)
from jose import (
    JWTError,
    ExpiredSignatureError,
)

from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.operations import user_ops
from CTFe.utils import jwt_utils
from CTFe.config import constants
from CTFe.config.database import dal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_ctx.verify(plain_password, hashed_password)


def hash_password(plain_password):
    return pwd_ctx.hash(plain_password)


def create_access_token(
    *,
    id: int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    payload = {}

    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta else
        datetime.utcnow() + timedelta(minutes=constants.JWT_EXPIRE_TIME)
    )

    issued_at = datetime.utcnow().timestamp()

    payload.update({"sub": str(id)})
    payload.update({"exp": expire})
    payload.update({"iat": issued_at})

    token = jwt_utils.encode(payload)

    return token


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(dal.get_session),
) -> user_schemas.UserDetails:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt_utils.decode(token)
    except ExpiredSignatureError:
        raise credentials_exception
    except JWTError:
        raise credentials_exception

    id = payload.get("sub")
    if id is None:
        raise credentials_exception

    conditions = and_(
        User.id == id,
    )

    db_user = user_ops.read_users_by_(session, conditions).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_details = user_schemas.UserDetails.from_orm(db_user)

    return user_details
