from fastapi import (
    FastAPI,
    Depends,
)

from CTFe.config.database import dal
from CTFe.utils import (
    enums,
    validators,
)
from CTFe.views import (
    auth_router,
    user_router,
)


app = FastAPI()

app.include_router(
    auth_router,
)
app.include_router(
    user_router,
    prefix="/users",
    dependencies=[
        Depends(validators.validate_admin),
    ]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("CTFe.main:app", host="0.0.0.0", port=8000, reload=True)
