from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str


class UserAuth(User):
    password: str


class UserInDB(User):
    hashed_password: str