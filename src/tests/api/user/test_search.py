import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_no_auth(async_client: AsyncClient, user):
    payload = {"username": ""}
    response = await async_client.post("/api/search", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_search_empty_query(async_client: AsyncClient, user):
    token = await async_client.post("/api/login", json={"username": "testuser", "password": "SecurePassword123!"})

    payload = {"username": ""}
    response = await async_client.post(
        "/api/search",
        json=payload,
        headers={"Authorization": f"Bearer {token.json()['access_token']}"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_success(async_client: AsyncClient, user):
    token = await async_client.post("/api/login", json={"username": "testuser", "password": "SecurePassword123!"})

    await async_client.post("/api/register", json={"username": "testuser-junior", "password": "123456"})
    await async_client.post("/api/register", json={"username": "senior-testuser", "password": "123456"})
    await async_client.post("/api/register", json={"username": "realuser", "password": "123456"})

    response = await async_client.post(
        "/api/search",
        json={"username": "testuser"},
        headers={"Authorization": f"Bearer {token.json()['access_token']}"}
    )
    assert response.status_code == 200
    assert [u["username"] for u in response.json()] == [
        "testuser",
        "testuser-junior",
        "senior-testuser",
    ]
