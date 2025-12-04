import requests
from tests.conftest import BASE_URL, TEST_ADMIN_PASSWORD

def test_login_and_me(admin_headers):
    resp = requests.get(f"{BASE_URL}/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"

def test_refresh(admin_headers):
    # Refresh-Token über Login holen
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD})
    refresh = login_resp.json()["refresh_token"]

    resp = requests.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and "refresh_token" in data

def test_logout(admin_headers):
    # Refresh-Token über Login holen
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD})
    refresh = login_resp.json()["refresh_token"]

    resp = requests.post(f"{BASE_URL}/auth/logout", json={"refresh_token": refresh})
    assert resp.status_code == 200

def test_login_invalid_credentials():
    """Test that login fails with invalid credentials."""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@example.com", "password": "WrongPassword123!"})
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.json()["detail"]

def test_expired_token_handling():
    """Test that expired tokens are properly rejected."""
    # This would require mocking token expiration or waiting,
    # but we can at least test that invalid tokens are rejected
    invalid_headers = {"Authorization": "Bearer invalid.token.here"}
    resp = requests.get(f"{BASE_URL}/auth/me", headers=invalid_headers)
    assert resp.status_code == 401
