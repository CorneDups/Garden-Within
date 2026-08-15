import json
import os

os.environ["INNER_GARDEN_DB_PATH"] = os.path.join(os.getcwd(), "tmp_sprint5_test.db")
if os.path.exists(os.environ["INNER_GARDEN_DB_PATH"]):
    os.remove(os.environ["INNER_GARDEN_DB_PATH"])

from fastapi.testclient import TestClient

import backend.main as main

main.configure_database_path(os.environ["INNER_GARDEN_DB_PATH"])
main.initialize_database()

client = TestClient(main.app)


def test_generate_and_persist_enneagram_hypothesis():
    register = client.post("/api/register", json={"username": "nina", "password": "secret123"})
    assert register.status_code == 201, register.text
    token = register.json()["token"]

    answers = {
        "answers": [
            {"question_number": 1, "question_text": "What do you want more freedom from?", "answer_text": "I want freedom from needing to prove my worth."},
            {"question_number": 2, "question_text": "What feels unresolved right now?", "answer_text": "I feel like I am always slightly outside my own life."},
            {"question_number": 3, "question_text": "What do you notice when you feel most exhausted?", "answer_text": "I shut down and become very private."},
            {"question_number": 4, "question_text": "What part of you feels most neglected?", "answer_text": "My emotional depth and sensitivity."},
            {"question_number": 5, "question_text": "What pattern repeats in your relationships?", "answer_text": "I over-invest and then feel unseen."},
            {"question_number": 6, "question_text": "What do you hope to be different by the end of this season?", "answer_text": "I want to feel more grounded and less like I have to disappear."},
        ]
    }

    submit = client.post("/api/onboarding/answers", headers={"Authorization": f"Bearer {token}"}, json=answers)
    assert submit.status_code == 200, submit.text

    response = client.post(
        "/api/enneagram/hypothesis",
        headers={"Authorization": f"Bearer {token}"},
        json={"answers": answers["answers"]},
    )
    assert response.status_code == 200, response.text

    payload = response.json()
    assert 1 <= payload["primary_type"] <= 9
    assert 1 <= payload["wing"] <= 9
    assert 0.0 <= payload["confidence"] <= 1.0
    assert set(payload["type_probabilities"].keys()) == {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
    assert payload["reasoning_summary"]

    stored = client.get("/api/enneagram/hypothesis", headers={"Authorization": f"Bearer {token}"})
    assert stored.status_code == 200, stored.text
    assert stored.json()["primary_type"] == payload["primary_type"]
    assert stored.json()["wing"] == payload["wing"]
