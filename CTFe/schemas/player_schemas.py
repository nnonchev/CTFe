from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    validator,
)


class TeamInvite(BaseModel):
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
    team_id: Optional[int] = None
    team_invites: List[TeamInvite]

    class Config:
        orm_mode = True


class Invites(BaseModel):
    team_invites: List[TeamInvite]

    class Config:
        orm_mode = True
