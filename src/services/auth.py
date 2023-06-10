from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from core.config import app_settings
from db.db import get_session
from exceptions.auth import CredentialException
from models import base as models
from schemas import base as schemas
from services.db import user_crud


SECRET_KEY = app_settings.secret_key
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_DAYS = 7


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> models.User | None:
    user: models.User | None = await user_crud.get(
        db=db,
        username=username
    )
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_session),
) -> schemas.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialException
    except JWTError:
        raise CredentialException
    user_in_db: models.User | None = await user_crud.get(
        db=db,
        username=username
    )
    if user_in_db is None:
        raise CredentialException
    return schemas.FullUser(
        username=username,
        id=user_in_db.id,
        uuid=user_in_db.uuid
    )


