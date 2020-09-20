from jose import (
    jwt,
    ExpiredSignatureError,
)
from fastapi import (
    status,
    HTTPException,
)

from CTFe.config import constants


def encode(payload):
    return jwt.encode(
        payload,
        constants.JWT_SECRET,
        algorithm=constants.JWT_ALGORITHM,
    )


def decode(token: str):
    return jwt.decode(
        token,
        constants.JWT_SECRET,
        algorithms=[constants.JWT_ALGORITHM],
    )
    try:
        payload = jwt.decode(
            token,

        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
        )
    else:
        return payload
