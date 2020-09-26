from typing import (
    List,
    Optional,
)

from pydantic import BaseModel

from CTFe.schemas import user_schemas


class Create(BaseModel):
    name: str


class Update(BaseModel):
    name: Optional[str] = None

    class Config:
        orm_mode = True


class Details(BaseModel):
    id: int
    name: str
    players: List[user_schemas.Details] = None

    class Config:
        orm_mode = True
