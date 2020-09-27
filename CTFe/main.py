from fastapi import (
    FastAPI,
    Depends,
)

from CTFe.config.database import dal
from CTFe.utils import (
    validators,
    enums,
)
from CTFe.views import (
    auth_router,
    user_router,
    team_router,
    challenge_router,
    attempt_router,
    player_router,
    contributor_router,
)


app = FastAPI()

app.include_router(
    auth_router,
)
app.include_router(
    user_router,
    prefix="/users",
    dependencies=[
        Depends(validators.validate_user_type(enums.UserType.ADMIN)),
    ],
)
app.include_router(
    team_router,
    prefix="/teams",
    dependencies=[
        Depends(validators.validate_user_type(enums.UserType.ADMIN)),
    ],
)
app.include_router(
    challenge_router,
    prefix="/challenges",
    dependencies=[
        Depends(validators.validate_user_type(enums.UserType.ADMIN)),
    ],
)
app.include_router(
    attempt_router,
    prefix="/attempts",
    dependencies=[
        Depends(validators.validate_user_type(enums.UserType.ADMIN)),
    ],
)
app.include_router(
    player_router,
    prefix="/players",
    dependencies=[
        Depends(validators.validate_user_type(enums.UserType.PLAYER)),
    ],
)
app.include_router(
    contributor_router,
    prefix="/contributors",
    dependencies=[
        Depends(validators.validate_user_type(enums.UserType.CONTRIBUTOR)),
    ],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("CTFe.main:app", host="0.0.0.0", port=8000, reload=True)
