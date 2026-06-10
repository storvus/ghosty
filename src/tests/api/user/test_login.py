import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "username,password",
    [
        ("incorrect_username", "SecurePassword123!"),
        ("", "SecurePassword123!"),
        ("testuser", "IncorrectPassword123!"),
        ("testuser", ""),
    ]
)
@pytest.mark.asyncio
async def test_invalid_username(async_client: AsyncClient, user, username: str, password: str):
    payload = {
        "password": password,
        "username": username
    }
    response = await async_client.post("/api/login", json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


@pytest.mark.asyncio
async def test_happy_path(async_client: AsyncClient, user):
    payload = {
        "password": "SecurePassword123!",
        "username": "testuser"
    }
    response = await async_client.post("/api/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
