from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    validator,
)


class Challenge(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Update(BaseModel):
    password: Optional[str] = None

    class Config:
        orm_mode = True


class Details(BaseModel):
    id: int
    username: str
    challenges: List[Challenge]

    class Config:
        orm_mode = True
