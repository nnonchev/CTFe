from typing import Optional

from pydantic import (
    BaseModel,
    validator,
)

from CTFe.utils import (
    enums,
    pwd_utils,
)


class UserLogin(BaseModel):
    username: str
    password: str

    # TODO Fix retarded solution
    @validator("password")
    def ensure_hashed_password(cls, v):
        return pwd_utils.hash_password(v)


class UserCreate(BaseModel):
    username: str
    password: str

    # TODO FIX RETARDED SOLUTION
    @validator("password")
    def ensure_hashed_password(cls, v):
        return pwd_utils.hash_password(v)


class UserUpdate(BaseModel):
    password: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        orm_mode = True

    # TODO FIX RETARDED SOLUTION!!!
    @validator("password")
    def ensure_hashed_password(cls, v):
        if v is not None:
            return pwd_utils.hash_password(v)

    @validator("user_type")
    def validate_user_type(cls, v):
        if not enums.UserType.has_type(v):
            raise ValueError(f"Incorrect user_type")
        return v


class UserDetails(BaseModel):
    id: int
    username: str
    user_type: enums.UserType
    team_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserRedisPayload(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
