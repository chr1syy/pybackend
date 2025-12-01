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
        data={"username": "admin", "password": "Admin123!Secure"}
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens

    # Zurücksetzen auf ein starkes Passwort für weitere Tests
    reset_resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": "Admin123!Secure", "new_password": "Admin123!Reset!"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert reset_resp.status_code == 200
    assert "Password changed" in reset_resp.json()["msg"]

    # Login mit Reset-Passwort prüfen
    reset_login = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "Admin123!Reset!"}
    )
    assert reset_login.status_code == 200
    reset_tokens = reset_login.json()
    assert "access_token" in reset_tokens
