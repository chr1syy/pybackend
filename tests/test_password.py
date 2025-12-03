import requests

BASE_URL = "http://localhost:8000"

def test_change_password_and_login(admin_headers):
    # Passwort ändern
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": "admin", "new_password": "Admin123!Secure"},
        headers=admin_headers
    )
    assert resp.status_code == 200
    assert "Password changed" in resp.json()["msg"]

    # Login mit neuem Passwort
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": "Admin123!Secure"}
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens

    