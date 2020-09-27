from typing import (
    List,
    Optional,
)

from pydantic import BaseModel


class TeamCaptain(BaseModel):
    id: int

    class Config:
        orm_mode = True


class TeamMember(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class MemberInvite(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Create(BaseModel):
    name: str


class Update(BaseModel):
    name: Optional[str] = None

    class Config:
        orm_mode = True


class Details(BaseModel):
    id: int
    name: str
    players: List[TeamMember] = None
    captain: Optional[TeamCaptain] = None
    player_invites: Optional[List[MemberInvite]] = None

    class Config:
        orm_mode = True
