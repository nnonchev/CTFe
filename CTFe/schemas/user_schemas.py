from typing import Optional

from pydantic import (
    BaseModel,
    validator,
)

from CTFe.utils import enums


class Login(BaseModel):
    username: str
    password: str


class Create(BaseModel):
    username: str
    password: str


class Update(BaseModel):
    password: Optional[str] = None
    user_type: Optional[str] = None

    class Config:
        orm_mode = True

    @validator("user_type")
    def validate_user_type(cls, v):
        if not enums.UserType.has_type(v):
            raise ValueError(f"Incorrect user_type")
        return v


class Details(BaseModel):
    id: int
    username: str
    user_type: enums.UserType

    class Config:
        orm_mode = True


class RedisPayload(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
