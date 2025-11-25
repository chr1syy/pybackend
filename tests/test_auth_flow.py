import requests

BASE_URL = "http://localhost:8000"

def test_login_and_me(admin_tokens):
    access = admin_tokens["access_token"]
    resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"

def test_refresh(admin_tokens):
    refresh = admin_tokens["refresh_token"]
    resp = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and "refresh_token" in data

def test_register_and_delete_user(admin_tokens):
    access = admin_tokens["access_token"]
    # User anlegen
    reg_resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": "alice", "password": "alice123", "role": "user"},
        headers={"Authorization": f"Bearer {access}"}
    )
    assert reg_resp.status_code == 200
    assert "created" in reg_resp.json()["msg"]

    # Login als alice
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "alice", "password": "alice123"})
    assert login_resp.status_code == 200
    alice_access = login_resp.json()["access_token"]

    # /me für alice
    me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {alice_access}"})
    assert me_resp.status_code == 200
    alice_id = me_resp.json()["id"]

    # Löschen durch Admin
    del_resp = requests.delete(f"{BASE_URL}/auth/users/{alice_id}", headers={"Authorization": f"Bearer {access}"})
    assert del_resp.status_code == 200
    assert "deleted" in del_resp.json()["msg"]

def test_logout(admin_tokens):
    refresh = admin_tokens["refresh_token"]
    resp = requests.post(f"{BASE_URL}/auth/logout", json={"refresh_token": refresh})
    assert resp.status_code == 200
