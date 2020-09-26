from typing import Optional

from pydantic import BaseModel


class Create(BaseModel):
    flag: str
    team_id: int
    challenge_id: int


class Details(BaseModel):
    id: int
    flag: str
    team_id: int
    challenge_id: int

    class Config:
        orm_mode = True
