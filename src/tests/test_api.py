import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.db import Base, get_session
from main import app


SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://test:test@localhost:5432/test'
TEST_USER = {
    'username': 'alex',
    'password': '123456'
}


async def override_get_session() -> AsyncSession:
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope='session')
def get_client():
    client = TestClient(app)
    return client


def test_user_creation(get_client):
    response = get_client.post(app.url_path_for('register'), json=TEST_USER)

    assert response.status_code == 201
    response_message = {
        'created': 'ok'
    }
    assert response.json() == response_message
