from fastapi import FastAPI

from CTFe.config.database import dal


app = FastAPI()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("CTFe.main:app", host="0.0.0.0", port=8000, reload=True)
