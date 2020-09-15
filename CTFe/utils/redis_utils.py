from datetime import (
    datetime,
    timedelta,
)
from contextlib import asynccontextmanager

import aioredis
from fastapi import (
    status,
    HTTPException,
)

from CTFe.schemas import user_schemas
from CTFe.utils import jwt_utils
from CTFe.config import constants


class RedisDataAccessLayer:
    def __init__(self):
        self.redis_url: str = None
        self.redis_db: int = None

    @asynccontextmanager
    async def get_redis_conn(self):
        """ Provide a transaction scope for redis """
        if self.redis_url is None:
            raise ValueError(f"Invalid redis url: { self.redis_url }")

        redis = await aioredis.create_redis_pool(self.redis_url, db=self.redis_db)

        try:
            yield redis
        finally:
            redis.close()
            await redis.wait_closed()


async def store_payload(
    user_payload: user_schemas.UserRedisPayload,
    redis_dal: RedisDataAccessLayer,
) -> str:
    """ Store user_payload in redis """
    id: int = user_payload.id

    sub = str(user_payload.id)
    iat = datetime.now().timestamp()
    exp = (datetime.now() + timedelta(minutes=constants.JWT_EXPIRE_TIME)).timestamp()

    payload = user_payload.json()

    async with redis_dal.get_redis_conn() as redis:
        await redis.set(id, payload, expire=constants.REDIS_EXPIRE)

    token = jwt_utils.encode({
        "sub": sub,
        "iat": iat,
        "exp": exp,
    })

    return token


async def retrieve_payload(
    token: str,
    redis_dal: RedisDataAccessLayer,
) -> user_schemas.UserRedisPayload:
    id: int = (
        int(
            jwt_utils
            .decode(token)
            .get("sub")
        )
    )

    async with redis_dal.get_redis_conn() as redis:
        payload = await redis.get(id)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Can not retrieve user",
        )

    user_payload = user_schemas.UserRedisPayload.parse_raw(payload)
    return user_payload


async def delete_key(
    id: int,
    redis_dal: RedisDataAccessLayer,
):
    async with redis_dal.get_redis_conn() as redis:
        await redis.delete(id)


redis_dal = RedisDataAccessLayer()
redis_dal.redis_url = constants.REDIS_ADDRESS
redis_dal.redis_db = constants.REDIS_DB_NAME
