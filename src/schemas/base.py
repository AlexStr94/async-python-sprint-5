from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel


class Ping(BaseModel):
    db: timedelta

class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str


class UserAuth(User):
    password: str


class UserInDB(User):
    hashed_password: str


class FullUser(User):
    id: int
    uuid: str


class FileUpdate(BaseModel):
    path: str
    size: int
    user_id: int


class File(FileUpdate):
    is_downloadable: bool = True
    uuid: str


class FileInDB(BaseModel):
    id: str
    name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool


class FileList(BaseModel):
    account_id: str
    files: List[FileInDB]