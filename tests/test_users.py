import requests

BASE_URL = "http://localhost:8000"

def test_list_users_as_admin(admin_headers):
    response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_admin_forbidden(admin_headers):
    users = requests.get(f"{BASE_URL}/users/", headers=admin_headers).json()
    admin_user = next(u for u in users if u["username"] == "admin")

    response = requests.delete(f"{BASE_URL}/users/{admin_user['id']}", headers=admin_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot delete admin user"
