import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.tests.factories import UserFactory


@pytest.mark.asyncio
async def test_search_no_auth(async_client: AsyncClient):
    response = await async_client.post("/api/search", json={"username": "x"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_search_empty_query(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.post("/api/search", json={"username": ""}, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_success(async_client: AsyncClient, db_session: AsyncSession, user, auth_headers: dict):
    extra_users = [
        UserFactory.build(username="userg"),
        UserFactory.build(username="userg-junior"),
        UserFactory.build(username="senior-userg"),
        UserFactory.build(username="realuser"),
    ]
    for u in extra_users:
        db_session.add(u)
    await db_session.commit()

    response = await async_client.post("/api/search", json={"username": "userg"}, headers=auth_headers)

    assert response.status_code == 200
    assert [u["username"] for u in response.json()] == [
        "userg",
        "userg-junior",
        "senior-userg",
    ]
