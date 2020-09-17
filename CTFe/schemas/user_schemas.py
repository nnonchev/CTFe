from typing import Optional

from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str
 

class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    password: Optional[str]
    user_type: Optional[str]

    class Config:
        orm_mode = True    


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
