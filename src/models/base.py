from sqlalchemy import Column, Integer, String, DateTime

from db.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    # token = Column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f'User {self.username}'