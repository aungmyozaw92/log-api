from fastapi import status


def test_register_login_profile(client):
    # Register
    payload = {
        "username": "alice",
        "password": "Secret@123",
        "name": "Alice",
        "email": "alice@example.com",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()["data"]["user"]
    assert data["username"] == "alice"

    # Login (OAuth2 form params)
    r2 = client.post(
        "/api/v1/auth/login",
        data={"username": "alice", "password": "Secret@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r2.status_code == status.HTTP_200_OK
    token = r2.json()["data"]["token"]["access_token"]
    assert token

    # Profile with bearer token
    r3 = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r3.status_code == status.HTTP_200_OK
    profile = r3.json()["data"]["user"]
    assert profile["username"] == "alice"


def test_users_crud(client):
    # Create
    r = client.post(
        "/api/v1/users/",
        json={
            "username": "bob",
            "password": "Passw0rd!",
            "name": "Bob",
            "email": "bob@example.com",
        },
    )
    assert r.status_code == status.HTTP_201_CREATED
    user = r.json()["data"]["user"]
    user_id = user["id"]

    # Get
    r2 = client.get(f"/api/v1/users/{user_id}")
    assert r2.status_code == status.HTTP_200_OK
    assert r2.json()["data"]["user"]["username"] == "bob"

    # List
    r3 = client.get("/api/v1/users/?limit=10&offset=0")
    assert r3.status_code == status.HTTP_200_OK
    assert isinstance(r3.json()["data"]["users"], list)

    # Update
    r4 = client.patch(
        f"/api/v1/users/{user_id}",
        json={"name": "Bobby", "is_active": True},
    )
    assert r4.status_code == status.HTTP_200_OK
    assert r4.json()["data"]["user"]["name"] == "Bobby"

    # Delete
    r5 = client.delete(f"/api/v1/users/{user_id}")
    assert r5.status_code == status.HTTP_200_OK
    r6 = client.get(f"/api/v1/users/{user_id}")
    assert r6.status_code == status.HTTP_404_NOT_FOUND


