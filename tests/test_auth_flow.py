import requests

BASE_URL = "http://localhost:8000"

def test_login_and_me(admin_headers):
    resp = requests.get(f"{BASE_URL}/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"

def test_refresh(admin_headers):
    # Refresh-Token über Login holen
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin"})
    refresh = login_resp.json()["refresh_token"]

    resp = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and "refresh_token" in data

def test_logout(admin_headers):
    # Refresh-Token über Login holen
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin"})
    refresh = login_resp.json()["refresh_token"]

    resp = requests.post(f"{BASE_URL}/auth/logout", json={"refresh_token": refresh})
    assert resp.status_code == 200
