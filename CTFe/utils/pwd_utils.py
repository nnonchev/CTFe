from passlib.context import CryptContext


pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_ctx.verify(plain_password, hashed_password)


def hash_password(plain_password):
    return pwd_ctx.hash(plain_password)
