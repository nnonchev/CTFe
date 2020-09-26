from typing import Optional

from pydantic import (
    BaseModel,
    validator,
)


class Update(BaseModel):
    password: Optional[str] = None

    class Config:
        orm_mode = True


class Details(BaseModel):
    id: int
    username: str
    team_id: Optional[int] = None

    class Config:
        orm_mode = True
