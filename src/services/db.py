from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union
import uuid

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services import auth
from db.db import Base
from models import base as models
from schemas import base as schemas
from exceptions import dp as exceptions


class Repository:

    def get(self, *args, **kwargs):
        raise NotImplementedError
    
    def create_or_update(self, *args, **kwargs):
        raise NotImplementedError

    def get_multi(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError
    

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class RepositoryUser(RepositoryDB[models.User, schemas.UserAuth, schemas.UserAuth]):
    async def create(self, db: AsyncSession, obj_in: schemas.UserAuth) -> ModelType:
        obj_in_data: dict = jsonable_encoder(obj_in)
        password: str = obj_in_data.pop('password')
        hashed_password = auth.get_password_hash(password)
        obj_in_data['hashed_password'] = hashed_password
        obj_in_data['uuid'] = uuid.uuid4().hex
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            raise exceptions.UserAlreadyExist
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, username: str) -> Optional[models.User]:
        statement = select(self._model).where(self._model.username == username)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    

class RepositoryFile(RepositoryDB[models.File, schemas.File, schemas.FileUpdate]):
    async def get(
        self,
        db: AsyncSession,
        user_id: int,
        path: str = '',
        uuid: str = '',
    ) -> Optional[models.File]:
        file_obj: Optional[models.File]

        if not user_id:
            raise exceptions.FieldError(field='user_id')
        if not path and not uuid:
            raise exceptions.FieldError(field='path or uuid')
        
        if uuid:
            statement = select(self._model). \
                where(
                    self._model.uuid == uuid,
                    self._model.user_id == user_id
                )
            results = await db.execute(statement=statement)
            file_obj = results.scalar_one_or_none()

            if file_obj: return file_obj
        
        if path:
            statement = select(self._model). \
                where(
                    self._model.path == path,
                    self._model.user_id == user_id
                )
            results = await db.execute(statement=statement)
            return results.scalar_one_or_none()
        
        return None
    
    async def update(
        self,
        db: AsyncSession,
        obj_in: schemas.FileUpdate
    ) -> models.File:
        obj_in_data = jsonable_encoder(obj_in)
        path = obj_in_data.get('path')
        user_id = obj_in_data.get('user_id')
        db_obj = await self.get(db, user_id=user_id, path=path)
        if db_obj:
            db_obj.size = obj_in_data.get('size')
            db_obj.created_at = datetime.utcnow()
            db.commit()
            return db_obj
        raise exceptions.FileDoesNotExist
        
    async def create_or_update(
        self,
        db: AsyncSession,
        obj_in: schemas.File
    ) -> Tuple[models.File, bool]:
        obj_in_data = jsonable_encoder(obj_in)
        path: str = obj_in_data.get('path')
        user_id = obj_in_data.get('user_id')
        db_obj: Optional[models.File] = await self.get(
            db=db,
            user_id=user_id,
            path=path
        )
        if db_obj:
            new_size = obj_in_data.get('size')
            db_obj = await self.update(
                db,
                schemas.FileUpdate(
                    path=path,
                    size=new_size,
                    user_id=user_id
                )
            )

            return db_obj, False

        db_obj = await self.create(db, obj_in)
        return db_obj, True
    
    async def get_multi(self,
        db: AsyncSession,
        user_id: int
    ) -> List[schemas.FileInDB]:
        statement = select(self._model).where(self._model.user_id == user_id)
        results = await db.execute(statement=statement)
        files_query = results.scalars()
        files = [
            schemas.FileInDB(
                id=file.uuid,
                name=file.path.split('/')[-1],
                created_at=file.created_at,
                path=file.path,
                size=file.size,
                is_downloadable=file.is_downloadable
            ) for file in files_query
        ]
        return files
     

user_crud = RepositoryUser(models.User)
file_crud = RepositoryFile(models.File)


async def db_ping(db: AsyncSession) -> Optional[timedelta]:
    statement = text('SELECT version();')
    start = datetime.utcnow()
    try:
        await db.execute(statement)
        ping = datetime.utcnow() - start
        return ping
    except ConnectionRefusedError:
        return None