from typing import Optional

from pydantic import (
    BaseModel,
    validator,
)

from CTFe.utils import enums


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    password: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        orm_mode = True

    @validator("user_type")
    def validate_user_type(cls, v):
        if not enums.UserType.has_type(v):
            raise ValueError(f"Incorrect user_type")
        return v


class UserDetails(BaseModel):
    id: int
    username: str
    team_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserRedisPayload(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
