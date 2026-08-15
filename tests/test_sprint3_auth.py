import os

os.environ["INNER_GARDEN_DB_PATH"] = os.path.join(os.getcwd(), "tmp_sprint3_test.db")
if os.path.exists(os.environ["INNER_GARDEN_DB_PATH"]):
    os.remove(os.environ["INNER_GARDEN_DB_PATH"])

from fastapi.testclient import TestClient

import backend.main as main

main.configure_database_path(os.environ["INNER_GARDEN_DB_PATH"])
main.initialize_database()

client = TestClient(main.app)


def test_register_login_logout_and_protected_access():
    register = client.post("/api/register", json={"username": "alice", "password": "secret123"})
    assert register.status_code == 201, register.text
    payload = register.json()
    assert payload["username"] == "alice"

    wrong_login = client.post("/api/login", json={"username": "alice", "password": "wrong-password"})
    assert wrong_login.status_code == 401, wrong_login.text

    login = client.post("/api/login", json={"username": "alice", "password": "secret123"})
    assert login.status_code == 200, login.text
    token = login.json()["token"]
    user_id = login.json()["user_id"]

    protected = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert protected.status_code == 200, protected.text
    assert protected.json()["user_id"] == user_id

    unauthenticated = client.get("/api/me")
    assert unauthenticated.status_code == 401, unauthenticated.text

    logout = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200, logout.text

    revoked = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert revoked.status_code == 401, revoked.text

    relogin = client.post("/api/login", json={"username": "alice", "password": "secret123"})
    assert relogin.status_code == 200, relogin.text
    assert relogin.json()["user_id"] == user_id
