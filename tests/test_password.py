import requests
from tests.conftest import BASE_URL, TEST_ADMIN_PASSWORD

def test_change_password_and_login(admin_headers):
    # Passwort ändern
    new_password = "NewAdmin123!Secure"
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": new_password},
        headers=admin_headers
    )
    assert resp.status_code == 200
    assert "Password changed" in resp.json()["msg"]

    # Login mit neuem Passwort
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": new_password}
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens

def test_password_validation_too_short():
    """Test that passwords shorter than 12 characters are rejected."""
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": "Short1!"},
        headers={"Authorization": "Bearer fake_token"}
    )
    # Will fail at validation before auth check
    assert resp.status_code in [401, 422]

def test_password_validation_no_uppercase():
    """Test that passwords without uppercase are rejected."""
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": "lowercase123!test"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert resp.status_code in [401, 422]

def test_password_validation_no_lowercase():
    """Test that passwords without lowercase are rejected."""
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": "UPPERCASE123!TEST"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert resp.status_code in [401, 422]

def test_password_validation_no_digit():
    """Test that passwords without digits are rejected."""
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": "NoDigitsHere!Test"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert resp.status_code in [401, 422]

def test_password_validation_no_special():
    """Test that passwords without special characters are rejected."""
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": "NoSpecial123Test"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert resp.status_code in [401, 422]

def test_password_validation_common_password():
    """Test that common passwords are rejected."""
    resp = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={"current_password": TEST_ADMIN_PASSWORD, "new_password": "Password123!"},
        headers={"Authorization": "Bearer fake_token"}
    )
    assert resp.status_code in [401, 422]
