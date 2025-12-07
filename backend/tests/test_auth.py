"""Authentication tests."""
import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123",  # Meets requirements: uppercase, lowercase, digit, 8+ chars
        "name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_weak_password(client):
    """Test that weak passwords are rejected."""
    response = await client.post("/api/auth/register", json={
        "email": "weak@example.com",
        "password": "weak",  # Too short, no uppercase, no digit
        "name": "Weak User"
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login(client):
    # First register and verify success
    register_res = await client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "LoginPass123"  # Meets requirements
    })
    assert register_res.status_code == 200

    # Then login
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "LoginPass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test that invalid credentials are rejected."""
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "WrongPass123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client):
    """Test that logout endpoint returns success message when authenticated."""
    # First register a user
    register_res = await client.post("/api/auth/register", json={
        "email": "logout@example.com",
        "password": "LogoutPass123",
        "name": "Logout User"
    })
    assert register_res.status_code == 200

    # Login to get an access token
    login_res = await client.post("/api/auth/login", json={
        "email": "logout@example.com",
        "password": "LogoutPass123"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    access_token = login_data["access_token"]

    # Use the token to logout
    response = await client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Successfully logged out"
