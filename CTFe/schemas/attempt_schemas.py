from typing import Optional

from pydantic import BaseModel


class AttemptCreate(BaseModel):
    flag: str
    team_id: int
    challenge_id: int


class AttemptUpdate(BaseModel):
    flag: Optional[str] = None
    team_id: Optional[int] = None
    challenge_id: Optional[int] = None

    class Config:
        orm_mode = True


class AttemptDetails(BaseModel):
    id: int
    flag: str
    team_id: int
    challenge_id: int

    class Config:
        orm_mode = True
