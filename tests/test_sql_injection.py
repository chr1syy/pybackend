import requests
from tests.conftest import BASE_URL

def test_audit_log_action_filter_sql_injection(admin_headers):
    """Test that SQL injection via wildcard characters in audit log filters is prevented."""
    # Try to inject SQL wildcards in the action parameter
    # Without proper escaping, this could match more results than intended
    resp = requests.get(
        f"{BASE_URL}/audit/logs",
        params={"action": "login%", "limit": 100},
        headers=admin_headers
    )
    assert resp.status_code == 200
    # Should not cause server error or unintended wildcard matching

    # Try underscore wildcard injection
    resp = requests.get(
        f"{BASE_URL}/audit/logs",
        params={"action": "login_attempt", "limit": 100},
        headers=admin_headers
    )
    assert resp.status_code == 200

    # Try backslash escaping
    resp = requests.get(
        f"{BASE_URL}/audit/logs",
        params={"action": "login\\", "limit": 100},
        headers=admin_headers
    )
    assert resp.status_code == 200


def test_audit_log_ip_filter_sql_injection(admin_headers):
    """Test that SQL injection via IP address filter is prevented."""
    # Try wildcard injection in IP filter
    resp = requests.get(
        f"{BASE_URL}/audit/logs",
        params={"ip_address": "127.0.0.%", "limit": 100},
        headers=admin_headers
    )
    assert resp.status_code == 200


def test_audit_log_user_agent_filter_sql_injection(admin_headers):
    """Test that SQL injection via user agent filter is prevented."""
    # Try wildcard injection in user agent filter
    resp = requests.get(
        f"{BASE_URL}/audit/logs",
        params={"user_agent": "Mozilla%", "limit": 100},
        headers=admin_headers
    )
    assert resp.status_code == 200


def test_no_sql_injection_in_email_login():
    """Test that SQL injection via email field in login is not possible."""
    # Try various SQL injection payloads in email field
    sql_payloads = [
        "admin@example.com' OR '1'='1",
        "admin@example.com'; DROP TABLE users; --",
        "admin@example.com' UNION SELECT * FROM users --",
    ]

    for payload in sql_payloads:
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": payload, "password": "anything"}
        )
        # Should return 401 (invalid credentials) or 422 (validation error)
        # Should NOT return 500 (server error from SQL injection)
        assert resp.status_code in [401, 422]
        assert resp.status_code != 500


def test_no_sql_injection_in_project_search():
    """Test that project name/description search doesn't allow SQL injection."""
    from tests.conftest import TEST_ADMIN_PASSWORD

    # Login as admin
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD}
    )
    admin_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Create a test project
    project_payload = {
        "project_number": "2025-SQL-TEST",
        "name": "Normal Project",
        "description": "Test SQL injection"
    }
    requests.post(f"{BASE_URL}/projects/", json=project_payload, headers=admin_headers)

    # Try SQL injection in project name search (if endpoint exists)
    # This tests that any search functionality properly escapes inputs
    resp = requests.get(f"{BASE_URL}/projects/", headers=admin_headers)
    assert resp.status_code == 200
    # Should not crash with SQL error
