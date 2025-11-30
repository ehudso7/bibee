"""Authentication tests."""
import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login(client):
    # First register
    await client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "testpass123"
    })

    # Then login
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
