import requests

BASE_URL = "http://localhost:8000"

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
