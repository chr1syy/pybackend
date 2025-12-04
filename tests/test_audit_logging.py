import requests
from tests.conftest import BASE_URL, TEST_ADMIN_PASSWORD

def test_audit_log_created_on_login(admin_headers):
    """Test that audit logs are created for login attempts."""
    # Get audit logs
    resp = requests.get(f"{BASE_URL}/audit/logs", params={"limit": 100}, headers=admin_headers)
    assert resp.status_code == 200
    logs = resp.json()

    # Check that login action is logged
    login_logs = [log for log in logs if "login" in log.get("action", "").lower()]
    assert len(login_logs) > 0, "No login audit logs found"

    # Verify log structure
    if login_logs:
        log = login_logs[0]
        assert "action" in log
        assert "ip_address" in log
        assert "user_agent" in log
        assert "success" in log
        assert "timestamp" in log


def test_audit_log_failed_login():
    """Test that failed login attempts are logged."""
    from tests.conftest import TEST_ADMIN_PASSWORD

    # Attempt failed login
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": "WrongPassword123!"}
    )
    assert resp.status_code == 401

    # Login as admin to check logs
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD}
    )
    admin_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Get audit logs
    resp = requests.get(f"{BASE_URL}/audit/logs", params={"success": False, "limit": 100}, headers=admin_headers)
    assert resp.status_code == 200
    logs = resp.json()

    # Check that failed login is logged
    failed_login_logs = [log for log in logs if "login" in log.get("action", "").lower() and not log["success"]]
    assert len(failed_login_logs) > 0, "No failed login audit logs found"


def test_audit_log_filters(admin_headers):
    """Test that audit log filtering works correctly."""
    # Test filtering by success
    resp = requests.get(f"{BASE_URL}/audit/logs", params={"success": True, "limit": 100}, headers=admin_headers)
    assert resp.status_code == 200
    logs = resp.json()
    if logs:
        assert all(log["success"] for log in logs)

    # Test filtering by action
    resp = requests.get(f"{BASE_URL}/audit/logs", params={"action": "login", "limit": 100}, headers=admin_headers)
    assert resp.status_code == 200
    logs = resp.json()
    if logs:
        assert all("login" in log["action"].lower() for log in logs)


def test_audit_log_admin_only_access():
    """Test that only admins can access audit logs."""
    from app.models import AccessCode
    from app.utils.db import SessionLocal

    # Create a non-admin user
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD}
    )
    admin_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    email = "regularuser@example.com"
    resp = requests.post(f"{BASE_URL}/auth/invite", params={"email": email}, headers=admin_headers)

    db = SessionLocal()
    code = db.query(AccessCode).filter_by(purpose="registration", used=False).first().code
    db.close()

    payload = {"code": code, "email": email, "username": "regularuser", "password": "Regular123!Secure"}
    requests.post(f"{BASE_URL}/auth/complete-registration", json=payload)

    # Login as regular user
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Regular123!Secure"})
    user_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Try to access audit logs as regular user
    resp = requests.get(f"{BASE_URL}/audit/logs", headers=user_headers)
    assert resp.status_code == 403, "Regular users should not be able to access audit logs"


def test_audit_log_contains_user_info():
    """Test that audit logs track user_id correctly."""
    # Login to generate audit log with user_id
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD}
    )
    assert resp.status_code == 200
    admin_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    # Get audit logs
    resp = requests.get(f"{BASE_URL}/audit/logs", params={"limit": 100}, headers=admin_headers)
    assert resp.status_code == 200
    logs = resp.json()

    # Find successful login logs that should have user_id
    successful_logins = [log for log in logs if "login" in log.get("action", "").lower() and log.get("success")]
    if successful_logins:
        # At least some successful logins should have user_id tracked
        assert any("user_id" in log for log in successful_logins), "Audit logs should track user_id"
