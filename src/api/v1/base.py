from datetime import timedelta
import mimetypes
import os
from typing import Annotated
import uuid
import aiofiles
from fastapi import APIRouter, Depends, Form, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from exceptions.dp import UserAlreadyExist
from models import base as models
from services.auth import ACCESS_TOKEN_EXPIRE_DAYS, authenticate_user, create_access_token, get_current_user
from services.db import user_crud, file_crud
from schemas import base as schemas

FILE_STORAGE = os.path.join(
    os.path.dirname(os.path.abspath(__name__)),
    'users_files'
)

router = APIRouter()


@router.post(
    '/register',
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


@router.post('/auth', response_model=schemas.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session)
) -> schemas.Token:
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
    return schemas.Token(
        access_token=access_token,
        token_type='bearer'
    )


@router.post(
    '/files/upload',
    status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file_in: UploadFile,
    path: Annotated[str, Form()],
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session)
) -> schemas.FileInDB:  
    if not file_in.size:
        raise Exception
    if not (file_type := file_in.content_type):
        raise Exception # add custom exception need type
    
    if not mimetypes.guess_all_extensions(file_type, strict=False):
        raise Exception # add custom exception type not supported
    
    file_type_in_path = mimetypes.guess_type(path, strict=False)[0]
    if (
        file_type_in_path
        and file_type_in_path != file_type
    ):
        raise Exception # add custom Exception
    
    if file_type_in_path:
        splited_path = path.split('/')
        file_name = splited_path[-1]
        catalog = '/'.join(splited_path[:-1])
    else:
        file_name = file_in.filename
        if not file_name:
            raise Exception
        catalog=path
        path = os.path.join(path, file_name)
    
    file = schemas.File(
        path=path,
        size=file_in.size,
        user_id=current_user.id,
        uuid=uuid.uuid4().hex
    )

    file_in_db, created = await file_crud.create_or_update(
        db=db, obj_in=file
    )

    catalog = f'{FILE_STORAGE}/{current_user.username}/{catalog}'
    os.makedirs(catalog, exist_ok=True)
    out_file_path = os.path.join(catalog, file_name)
    if not created:
        os.remove(out_file_path)
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file_in.read()  # async read
        await out_file.write(content)

    return schemas.FileInDB(
        id=file_in_db.uuid,
        name=file_in_db.path.split('/')[-1],
        created_at=file_in_db.created_at,
        path=file_in_db.path,
        size=file_in_db.size,
        is_downloadable=file_in_db.is_downloadable
    )


@router.get(
        '/files/download',
        status_code=status.HTTP_200_OK,
)
async def download_file(
    path: str,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    if not '.' in path:
        _uuid = path
        file = await file_crud.get(
            db,
            user_id=current_user.id,
            uuid=_uuid
        )
    else:
        file = await file_crud.get(
            db,
            user_id=current_user.id,
            path=path
        )
    if not file:
        raise Exception # add custom exception
    
    file_type = mimetypes.guess_type(file.path, strict=False)[0]

    file_path = f'{FILE_STORAGE}/{current_user.username}/{file.path}'

    def iterfile():  # 
        with open(file_path, mode="rb") as file_like:  # 
            yield from file_like  #

    return StreamingResponse(iterfile(), media_type=file_type)
    

@router.get(
    '/files',
    status_code=status.HTTP_200_OK
)
async def get_files_list(
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
) -> schemas.FileList:
    files = await file_crud.get_multi(db, current_user.id)
    return schemas.FileList(
        account_id=current_user.uuid,
        files=files
    )