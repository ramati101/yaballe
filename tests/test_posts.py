import pytest

@pytest.mark.asyncio
async def test_create_and_list_posts(client):
    # Register user to get token
    await client.post("/auth/register", json={
        "username": "postuser4",
        "password": "password123"
    })
    login_res = await client.post("/auth/login", json={
        "username": "postuser4",
        "password": "password123"
    })
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create post
    post_data = {"title": "My Test Post", "content": "Content here"}
    res = await client.post("/posts/", json=post_data, headers=headers)
    assert res.status_code == 201
    post = res.json()
    assert post["title"] == "My Test Post"

    # List posts
    res = await client.get("/posts/", headers=headers)
    assert res.status_code == 200
    posts = res.json()
    assert len(posts) >= 1

@pytest.mark.asyncio
async def test_create_post_unauthorized(client):
    res = await client.post("/posts/", json={
        "title": "Unauthorized",
        "content": "Should fail"
    })
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_list_posts_unauthorized(client):
    res = await client.get("/posts/")
    assert res.status_code == 401