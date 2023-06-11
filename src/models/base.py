from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    files = relationship('File', back_populates='user')
    uuid = Column(String(100), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f'User {self.username}'
    

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, index=True, default=datetime.utcnow) 
    path = Column(String(300), unique=True, nullable=False)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates="files")
    uuid = Column(String(100), unique=True, nullable=False)
