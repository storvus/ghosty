import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    payload = {"password": "SecurePassword123!", "username": "newuser"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_register_duplicate_username(async_client: AsyncClient):
    payload = {"password": "SecurePassword123!", "username": "user1"}
    await async_client.post("/api/register", json=payload)

    response = await async_client.post("/api/register", json={**payload, "password": "DifferentPassword456!"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Username already taken"}


@pytest.mark.asyncio
async def test_register_null_fields(async_client: AsyncClient):
    response = await async_client.post("/api/register", json={"password": None, "username": None})
    assert response.status_code == 422
    details = [(d["msg"], d["loc"]) for d in response.json()["detail"]]
    assert ("Input should be a valid string", ["body", "username"]) in details
    assert ("Input should be a valid string", ["body", "password"]) in details


@pytest.mark.asyncio
async def test_register_too_short_fields(async_client: AsyncClient):
    response = await async_client.post("/api/register", json={"password": "1q2w3", "username": "yu"})
    assert response.status_code == 422
    details = [(d["msg"], d["input"]) for d in response.json()["detail"]]
    assert ("String should have at least 3 characters", "yu") in details
    assert ("String should have at least 6 characters", "1q2w3") in details


@pytest.mark.asyncio
async def test_register_username_too_long(async_client: AsyncClient):
    response = await async_client.post("/api/register", json={"password": "1q2w3e", "username": "y" * 50})
    assert response.status_code == 422
    assert "String should have at most 32 characters" in [d["msg"] for d in response.json()["detail"]]


@pytest.mark.asyncio
async def test_register_missing_fields(async_client: AsyncClient):
    response = await async_client.post("/api/register", json={})
    assert response.status_code == 422
    details = [(d["msg"], d["loc"]) for d in response.json()["detail"]]
    assert ("Field required", ["body", "username"]) in details
    assert ("Field required", ["body", "password"]) in details


@pytest.mark.asyncio
async def test_register_password_is_hashed(async_client: AsyncClient, db_session: AsyncSession):
    payload = {"password": "SecurePassword123!", "username": "hashuser"}
    response = await async_client.post("/api/register", json=payload)
    assert response.status_code == 201

    result = await db_session.execute(select(User).where(User.username == "hashuser"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.password_hash != payload["password"]
