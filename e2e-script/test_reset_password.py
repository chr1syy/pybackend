import requests

BASE_URL = "http://localhost:8000"

def main():
    # 1. Mailadresse für Passwort-Reset abfragen
    email = input("Bitte Mailadresse für Passwort-Reset eingeben: ").strip()

    # 2. Forgot-Password Endpoint aufrufen
    resp = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": email}
    )
    if resp.status_code != 200:
        print("Forgot-Password fehlgeschlagen:", resp.text)
        return
    print("Reset-Mail angefordert:", resp.json())

    # 3. Zugangscode eingeben (normalerweise aus Mail, hier manuell oder aus DB)
    code = input("Bitte Reset-Code eingeben (aus Mail oder DB): ").strip()

    # 4. Neues Dummy-Passwort setzen
    new_password = "new_dummy_password123"
    resp = requests.post(
        f"{BASE_URL}/auth/reset-password",
        json={"email": email, "code": code, "new_password": new_password}
    )

    if resp.status_code != 200:
        print("Reset fehlgeschlagen:", resp.text)
        return

    print("Passwort erfolgreich zurückgesetzt:", resp.json())

    # 5. Test: Login mit neuem Passwort
    login_data = {"username": email, "password": new_password}
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code == 200:
        print("Login mit neuem Passwort erfolgreich:", resp.json())
    else:
        print("Login mit neuem Passwort fehlgeschlagen:", resp.text)


if __name__ == "__main__":
    main()
