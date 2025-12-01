import requests

BASE_URL = "http://localhost:8000"

def test_list_users_as_admin(admin_headers):
    response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_register_user_success(admin_headers):
    payload = {"username": "newuser", "password": "secret", "role": "user"}
    response = requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert "created" in response.json()["detail"]

    # Login als newuser
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "newuser", "password": "secret"})
    assert login_resp.status_code == 200
    newuser_access = login_resp.json()["access_token"]

    # /me für newuser
    me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {newuser_access}"})
    assert me_resp.status_code == 200
    newuser_id = me_resp.json()["id"]

    # Löschen durch Admin
    del_resp = requests.delete(f"{BASE_URL}/users/{newuser_id}", headers=admin_headers)
    assert del_resp.status_code == 200
    assert "deleted" in del_resp.json()["detail"]

def test_register_user_duplicate(admin_headers):
    payload = {"username": "newuser", "password": "secret", "role": "user"}
    requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)
    response = requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

def test_register_user_forbidden(admin_headers):
    payload = {"username": "newuser", "password": "secret", "role": "user"}
    response = requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert "created" in response.json()["detail"]

    # Login als newuser
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "newuser", "password": "secret"})
    assert login_resp.status_code == 200
    newuser_access = login_resp.json()["access_token"]

    # /me für newuser
    me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {newuser_access}"})
    assert me_resp.status_code == 200
    newuser_id = me_resp.json()["id"]

    # Register as newuser
    payload = {"username": "newuser", "password": "secret", "role": "user"}
    response = requests.post(f"{BASE_URL}/users/register", json=payload, headers={"Authorization": f"Bearer {newuser_access}"})
    assert response.status_code == 403

    # Löschen durch Admin
    del_resp = requests.delete(f"{BASE_URL}/users/{newuser_id}", headers=admin_headers)
    assert del_resp.status_code == 200
    assert "deleted" in del_resp.json()["detail"]

def test_register_user_duplicate(admin_headers):
    payload = {"username": "newuser", "password": "secret", "role": "user"}
    requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)
    response = requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

def test_update_user_role_success(admin_headers):
    payload = {"username": "roleuser", "password": "secret", "role": "user"}
    requests.post(f"{BASE_URL}/users/register", json=payload, headers=admin_headers)

    # User-ID über /users holen
    users = requests.get(f"{BASE_URL}/users/", headers=admin_headers).json()
    user_id = next(u["id"] for u in users if u["username"] == "roleuser")

    response = requests.put(f"{BASE_URL}/users/{user_id}", json={"role": "admin"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "admin"

def test_delete_admin_forbidden(admin_headers):
    users = requests.get(f"{BASE_URL}/users/", headers=admin_headers).json()
    admin_user = next(u for u in users if u["username"] == "admin")

    response = requests.delete(f"{BASE_URL}/users/{admin_user['id']}", headers=admin_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot delete admin user"
