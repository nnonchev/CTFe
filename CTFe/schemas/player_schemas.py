from typing import Optional

from pydantic import (
    BaseModel,
    validator,
)


class PlayerUpdate(BaseModel):
    password: Optional[str] = None

    class Config:
        orm_mode = True


class PlayerDetails(BaseModel):
    id: int
    username: str
    team_id: Optional[int] = None

    class Config:
        orm_mode = True
