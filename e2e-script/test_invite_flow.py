import requests

BASE_URL = "http://localhost:8000"

def main():
    # 1. Login als Admin
    login_data = {
        "username": "admin@example.com",  # Admin-Mailadresse
        "password": "admin"               # Admin-Passwort
    }
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code != 200:
        print("Login fehlgeschlagen:", resp.text)
        return

    tokens = resp.json()
    access_token = tokens["access_token"]
    print("Login erfolgreich, AccessToken erhalten.")

    # 2. Mailadresse für Einladung abfragen
    email = input("Bitte Mailadresse für Einladung eingeben: ").strip()

    # 3. Einladung senden
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post(f"{BASE_URL}/auth/invite", params={"email": email}, headers=headers)

    if resp.status_code != 200:
        print("Invite fehlgeschlagen:", resp.text)
        return

    invite_result = resp.json()
    print("Invite erfolgreich:", invite_result)

    # 4. Dummy-Registrierung simulieren (normalerweise macht das der eingeladene User)
    # Hier nehmen wir den Code aus der Mailantwort (in Tests kannst du den direkt aus DB holen)
    code = input("Bitte Zugangscode eingeben (aus Invite-Mail oder DB): ").strip()
    dummy_password = "dummy123"
    dummy_user = "dummyuser"

    resp = requests.post(
        f"{BASE_URL}/auth/complete-registration",
        json={"email": email, "username": dummy_user, "code": code, "password": dummy_password}
    )

    if resp.status_code != 200:
        print("Registrierung fehlgeschlagen:", resp.text)
        return

    print("Dummy-Nutzer erfolgreich registriert:", resp.json())


if __name__ == "__main__":
    main()
