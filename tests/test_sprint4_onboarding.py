import os

os.environ["INNER_GARDEN_DB_PATH"] = os.path.join(os.getcwd(), "tmp_sprint4_test.db")
if os.path.exists(os.environ["INNER_GARDEN_DB_PATH"]):
    os.remove(os.environ["INNER_GARDEN_DB_PATH"])

from fastapi.testclient import TestClient

import backend.main as main

main.configure_database_path(os.environ["INNER_GARDEN_DB_PATH"])
main.initialize_database()

client = TestClient(main.app)


def test_register_then_complete_onboarding_and_keep_it_persistent():
    register = client.post("/api/register", json={"username": "maya", "password": "secret123"})
    assert register.status_code == 201, register.text
    token = register.json()["token"]

    questions = client.get("/api/onboarding/questions", headers={"Authorization": f"Bearer {token}"})
    assert questions.status_code == 200, questions.text
    question_list = questions.json()["questions"]
    assert len(question_list) == 7
    assert all("question" in item for item in question_list)

    answers_payload = {
        "answers": [
            {"question_number": 1, "question_text": "What do you want more freedom from?", "answer_text": "The pressure to be useful."},
            {"question_number": 2, "question_text": "What feels unresolved right now?", "answer_text": "I want to trust my own pace."},
            {"question_number": 3, "question_text": "What do you notice when you feel most exhausted?", "answer_text": "I stop listening to myself."},
            {"question_number": 4, "question_text": "What part of you feels most neglected?", "answer_text": "My inner quiet."},
            {"question_number": 5, "question_text": "What pattern repeats in your relationships?", "answer_text": "I overgive to be accepted."},
            {"question_number": 6, "question_text": "What do you hope to be different by the end of this season?", "answer_text": "I want to feel grounded and self-trusting."},
            {"question_number": 7, "question_text": "What has recently happened that bothered you or felt like a calling for you to explore?", "answer_text": "I started saying yes to everyone and lost my center."},
        ]
    }

    submit = client.post("/api/onboarding/answers", headers={"Authorization": f"Bearer {token}"}, json=answers_payload)
    assert submit.status_code == 200, submit.text
    assert submit.json()["status"] == "saved"

    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    assert me.json()["onboarding_complete"] is True

    after_submit = client.get("/api/onboarding/questions", headers={"Authorization": f"Bearer {token}"})
    assert after_submit.status_code == 200, after_submit.text
    assert after_submit.json()["questions"] == []

    login_again = client.post("/api/login", json={"username": "maya", "password": "secret123"})
    assert login_again.status_code == 200, login_again.text
    second_token = login_again.json()["token"]

    status_again = client.get("/api/me", headers={"Authorization": f"Bearer {second_token}"})
    assert status_again.status_code == 200, status_again.text
    assert status_again.json()["onboarding_complete"] is True

    questions_again = client.get("/api/onboarding/questions", headers={"Authorization": f"Bearer {second_token}"})
    assert questions_again.status_code == 200, questions_again.text
    assert questions_again.json()["questions"] == []
