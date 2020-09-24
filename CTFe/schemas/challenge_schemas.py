from typing import (
    List,
    Optional,
)

from pydantic import BaseModel


class ChallengeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    flag: str
    file_name: Optional[str] = None


class ChallengeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    flag: Optional[str] = None
    file_name: Optional[str] = None

    class Config:
        orm_mode = True


class ChallengeDetails(BaseModel):
    id: int
    name: str
    description: str
    flag: str
    file_name: Optional[str] = None
    owner_id: int

    class Config:
        orm_mode = True
