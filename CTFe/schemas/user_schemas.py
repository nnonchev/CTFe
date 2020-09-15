from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserDetails(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class UserRedisPayload(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
