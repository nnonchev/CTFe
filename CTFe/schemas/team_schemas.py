from typing import List, Optional

from pydantic import BaseModel

from CTFe.schemas import user_schemas


class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    players: List[user_schemas.UserDetails] = None

    class Config:
        orm_mode = True


class TeamDetails(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
