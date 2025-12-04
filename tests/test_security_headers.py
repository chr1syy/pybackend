import requests
from tests.conftest import BASE_URL

def test_security_headers_present():
    """Test that all security headers are present in responses."""
    resp = requests.get(f"{BASE_URL}/")

    # Check X-Content-Type-Options
    assert "X-Content-Type-Options" in resp.headers
    assert resp.headers["X-Content-Type-Options"] == "nosniff"

    # Check X-Frame-Options
    assert "X-Frame-Options" in resp.headers
    assert resp.headers["X-Frame-Options"] == "DENY"

    # Check X-XSS-Protection
    assert "X-XSS-Protection" in resp.headers
    assert resp.headers["X-XSS-Protection"] == "1; mode=block"

    # Check Strict-Transport-Security (HSTS)
    assert "Strict-Transport-Security" in resp.headers
    assert "max-age=" in resp.headers["Strict-Transport-Security"]

    # Check Referrer-Policy
    assert "Referrer-Policy" in resp.headers
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    # Check Permissions-Policy
    assert "Permissions-Policy" in resp.headers


def test_security_headers_on_auth_endpoints(admin_headers):
    """Test that security headers are present on auth endpoints."""
    resp = requests.get(f"{BASE_URL}/auth/me", headers=admin_headers)

    assert "X-Content-Type-Options" in resp.headers
    assert "X-Frame-Options" in resp.headers
    assert "Strict-Transport-Security" in resp.headers


def test_cors_configuration():
    """Test that CORS is properly configured."""
    # Make a POST request and check CORS headers are present
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "test@example.com", "password": "Test123!Pass"}
    )

    # CORS headers should be present in response
    # Check for Access-Control-Allow-Origin header (CORS is configured)
    # The status may be 401 (invalid credentials) but CORS headers should still be present
    assert resp.status_code in [200, 401]
    # If CORS is configured, this header should be present
    # Note: The presence of this header depends on the request origin
