import pytest

@pytest.mark.asyncio
async def test_register_and_login(client):
    response = await client.post("/auth/register", json={
        "username": "testuser5",
        "password": "testpass"
    })
    assert response.status_code == 201
    token = response.json()["access_token"]
    assert token

    response = await client.post("/auth/login", json={
        "username": "testuser5",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_with_wrong_password(client):
    # Register
    await client.post("/auth/register", json={
        "username": "wrongpassuser1",
        "password": "correct123"
    })

    # Try login with wrong password
    res = await client.post("/auth/login", json={
        "username": "wrongpassuser1",
        "password": "wrong123"
    })

    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_register_with_existing_username(client):
    payload = {"username": "duplicateuser", "password": "123456"}
    await client.post("/auth/register", json=payload)
    res = await client.post("/auth/register", json=payload)

    assert res.status_code == 400
    assert res.json()["detail"] == "Username already taken"

@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    res = await client.post("/auth/login", json={
        "username": "ghost",
        "password": "nothing"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"