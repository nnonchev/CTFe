from typing import (
    List,
    Optional,
)

from pydantic import BaseModel


class Create(BaseModel):
    name: str
    description: Optional[str] = None
    flag: str
    owner_id: Optional[int] = None


class Update(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    flag: Optional[str] = None
    file_name: Optional[str] = None

    class Config:
        orm_mode = True


class Details(BaseModel):
    id: int
    name: str
    description: str
    flag: str
    file_name: Optional[str] = None
    owner_id: Optional[int]

    class Config:
        orm_mode = True
