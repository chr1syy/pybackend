import requests

BASE_URL = "http://localhost:8000"

def show_audit_logs(token: str, limit: int = 20):
    url = f"{BASE_URL}/audit/logs?limit={limit}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
        return

    logs = resp.json()
    print(f"\n=== Showing last {len(logs)} AuditLogs ===")
    for log in logs:
        print(
            f"[{log['timestamp']}] user_id={log['user_id']} "
            f"action={log['action']} ip={log['ip_address']}"
        )

if __name__ == "__main__":
    # Admin Login zuerst
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "Admin123!Reset!"}
    )
    if login_resp.status_code != 200:
        print("Admin login failed:", login_resp.text)
    else:
        tokens = login_resp.json()
        access_token = tokens["access_token"]
        show_audit_logs(access_token, limit=20)
