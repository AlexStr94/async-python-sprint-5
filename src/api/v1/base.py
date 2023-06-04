from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from exceptions.dp import UserAlreadyExist
from models import base as models
from services.auth import ACCESS_TOKEN_EXPIRE_DAYS, authenticate_user, create_access_token
from services.db import user_crud
from schemas import base as schemas


router = APIRouter()


@router.post(
    '/register/',
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: schemas.UserAuth,
    db: AsyncSession = Depends(get_session)
):
    try:
        user: models.User = await user_crud.create(db=db, obj_in=user_in)
    except UserAlreadyExist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with this username already exist'
        )
    
    return


@router.post("/auth", response_model=schemas.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session)
):
    user: models.User | None = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}