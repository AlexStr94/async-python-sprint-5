from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import uuid

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.dp import UserAlreadyExist

from services import auth
from db.db import Base
from models import base as models
from schemas import base as schemas


class Repository:

    def get(self, *args, **kwargs):
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


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class RepositoryUser(RepositoryDB[models.User, schemas.UserAuth]):
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
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
            raise UserAlreadyExist
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, username: str) -> Optional[models.User]:
        statement = select(self._model).where(self._model.username == username)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()
    

class RepositoryFile(RepositoryDB[models.File, schemas.File]):
    pass


user_crud = RepositoryUser(models.User)
file_crud = RepositoryFile(models.File)