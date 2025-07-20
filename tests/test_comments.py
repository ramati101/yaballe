import pytest

@pytest.mark.asyncio
async def test_create_and_get_comments(client):
    # Register + login
    await client.post("/auth/register", json={
        "username": "commentuser3",
        "password": "pass1234"
    })
    login_res = await client.post("/auth/login", json={
        "username": "commentuser3",
        "password": "pass1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create post
    post_res = await client.post("/posts/", json={
        "title": "Post with Comments",
        "content": "This post will have comments"
    }, headers=headers)
    post_id = post_res.json()["id"]

    # Add comment
    comment_data = {"post_id": post_id, "content": "Great post!"}
    res = await client.post("/comments/", json=comment_data, headers=headers)
    assert res.status_code == 201
    comment = res.json()
    assert comment["content"] == "Great post!"

    # Get comments
    res = await client.get(f"/comments/post/{post_id}", headers=headers)
    assert res.status_code == 200
    comments = res.json()
    assert len(comments) == 1

@pytest.mark.asyncio
async def test_comment_on_nonexistent_post(client):
    # Register and login
    await client.post("/auth/register", json={
        "username": "no_post_user",
        "password": "pass1234"
    })
    login_res = await client.post("/auth/login", json={
        "username": "no_post_user",
        "password": "pass1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Comment on fake post_id
    res = await client.post("/comments/", json={
        "post_id": "nonexistent-id",
        "content": "This should fail"
    }, headers=headers)

    assert res.status_code == 404  # Assuming you return 404 on missing post