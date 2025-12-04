import requests
from tests.conftest import BASE_URL

def test_create_project_success(admin_headers):
    payload = {
        "project_number": "2025-0001",
        "name": "Testprojekt",
        "description": "Kurzbeschreibung für Testprojekt"
    }
    resp = requests.post(f"{BASE_URL}/projects/", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_number"] == "2025-0001"
    assert data["name"] == "Testprojekt"
    assert data["description"] == "Kurzbeschreibung für Testprojekt"
    assert "id" in data
    # Note: owner_id is tracked in the database but not exposed in the response schema

def test_create_project_duplicate_number(admin_headers):
    payload = {
        "project_number": "2025-0002",
        "name": "Projekt A",
        "description": "Beschreibung A"
    }
    # Erstes Projekt anlegen
    requests.post(f"{BASE_URL}/projects/", json=payload, headers=admin_headers)

    # Zweites Projekt mit gleicher Nummer
    resp = requests.post(f"{BASE_URL}/projects/", json=payload, headers=admin_headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Project number already exists"

def test_list_projects(admin_headers):
    resp = requests.get(f"{BASE_URL}/projects/", headers=admin_headers)
    assert resp.status_code == 200
    projects = resp.json()
    assert isinstance(projects, list)

def test_get_project_by_id(admin_headers):
    # Projekt anlegen
    payload = {
        "project_number": "2025-0003",
        "name": "Projekt B",
        "description": "Beschreibung B"
    }
    create_resp = requests.post(f"{BASE_URL}/projects/", json=payload, headers=admin_headers)
    project_id = create_resp.json()["id"]

    # Projekt abrufen
    resp = requests.get(f"{BASE_URL}/projects/{project_id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == project_id
    assert data["project_number"] == "2025-0003"

def test_update_project(admin_headers):
    # Projekt anlegen
    payload = {
        "project_number": "2025-0004",
        "name": "Projekt C",
        "description": "Beschreibung C"
    }
    create_resp = requests.post(f"{BASE_URL}/projects/", json=payload, headers=admin_headers)
    project_id = create_resp.json()["id"]

    # Update
    update_payload = {"name": "Projekt C Updated", "description": "Neue Beschreibung"}
    resp = requests.put(f"{BASE_URL}/projects/{project_id}", json=update_payload, headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Projekt C Updated"
    assert data["description"] == "Neue Beschreibung"

def test_delete_project(admin_headers):
    # Projekt anlegen
    payload = {
        "project_number": "2025-0005",
        "name": "Projekt D",
        "description": "Beschreibung D"
    }
    create_resp = requests.post(f"{BASE_URL}/projects/", json=payload, headers=admin_headers)
    project_id = create_resp.json()["id"]

    # Löschen
    resp = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert "deleted" in resp.json()["msg"]

    # Abruf nach Löschen → 404
    resp2 = requests.get(f"{BASE_URL}/projects/{project_id}", headers=admin_headers)
    assert resp2.status_code == 404
    assert resp2.json()["detail"] == "Project not found"


def test_collaborative_access(admin_headers, db_session):
    """Test that all users can view and edit projects (collaborative environment)."""
    from app.models import User, AccessCode
    from app.auth.routes import send_email
    import pytest

    # Create a second user
    email = "collaborator@example.com"

    # 1. Admin invites collaborator
    resp = requests.post(f"{BASE_URL}/auth/invite", params={"email": email}, headers=admin_headers)
    assert resp.status_code == 200

    # 2. Get registration code
    code = db_session.query(AccessCode).filter_by(purpose="registration", used=False).first().code

    # 3. Complete registration
    payload = {"code": code, "email": email, "username": "collaborator", "password": "Collab123!Secure"}
    resp = requests.post(f"{BASE_URL}/auth/complete-registration", json=payload)
    assert resp.status_code == 200

    # 4. Login as collaborator
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Collab123!Secure"})
    collab_token = login_resp.json()["access_token"]
    collab_headers = {"Authorization": f"Bearer {collab_token}"}

    # 5. Admin creates a project
    project_payload = {
        "project_number": "2025-COLLAB",
        "name": "Collaborative Project",
        "description": "Test collaborative access"
    }
    create_resp = requests.post(f"{BASE_URL}/projects/", json=project_payload, headers=admin_headers)
    assert create_resp.status_code == 200
    project_id = create_resp.json()["id"]

    # 6. Collaborator can VIEW the project
    view_resp = requests.get(f"{BASE_URL}/projects/{project_id}", headers=collab_headers)
    assert view_resp.status_code == 200
    assert view_resp.json()["name"] == "Collaborative Project"

    # 7. Collaborator can LIST projects (including admin's projects)
    list_resp = requests.get(f"{BASE_URL}/projects/", headers=collab_headers)
    assert list_resp.status_code == 200
    projects = list_resp.json()
    assert any(p["id"] == project_id for p in projects)

    # 8. Collaborator can EDIT the project
    update_payload = {"name": "Updated by Collaborator", "description": "Changed"}
    update_resp = requests.put(f"{BASE_URL}/projects/{project_id}", json=update_payload, headers=collab_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated by Collaborator"

    # 9. Collaborator CANNOT DELETE the project (not owner or admin)
    delete_resp = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=collab_headers)
    assert delete_resp.status_code == 403
    assert "Not authorized" in delete_resp.json()["detail"]

    # 10. Admin CAN DELETE the project (is owner)
    delete_resp = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=admin_headers)
    assert delete_resp.status_code == 200


def test_owner_can_delete_own_project(db_session):
    """Test that project owner can delete their own project."""
    from app.models import AccessCode

    # Create a user
    email = "owner@example.com"

    # 1. Create admin headers for invite
    from tests.conftest import TEST_ADMIN_PASSWORD
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@example.com", "password": TEST_ADMIN_PASSWORD})
    admin_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    resp = requests.post(f"{BASE_URL}/auth/invite", params={"email": email}, headers=admin_headers)
    code = db_session.query(AccessCode).filter_by(purpose="registration", used=False).first().code

    # 2. Complete registration
    payload = {"code": code, "email": email, "username": "owner", "password": "Owner123!Secure"}
    requests.post(f"{BASE_URL}/auth/complete-registration", json=payload)

    # 3. Login as owner
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Owner123!Secure"})
    owner_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # 4. Owner creates a project
    project_payload = {
        "project_number": "2025-OWNER",
        "name": "Owner's Project",
        "description": "Test owner deletion"
    }
    create_resp = requests.post(f"{BASE_URL}/projects/", json=project_payload, headers=owner_headers)
    assert create_resp.status_code == 200
    project_id = create_resp.json()["id"]

    # 5. Owner can delete their own project
    delete_resp = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=owner_headers)
    assert delete_resp.status_code == 200
