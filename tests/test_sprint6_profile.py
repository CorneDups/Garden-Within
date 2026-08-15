import os

os.environ["INNER_GARDEN_DB_PATH"] = os.path.join(os.getcwd(), "tmp_sprint6_test.db")
if os.path.exists(os.environ["INNER_GARDEN_DB_PATH"]):
    os.remove(os.environ["INNER_GARDEN_DB_PATH"])

from fastapi.testclient import TestClient

import backend.main as main

main.configure_database_path(os.environ["INNER_GARDEN_DB_PATH"])
main.initialize_database()

client = TestClient(main.app)


def test_generate_and_persist_player_profile():
    register = client.post("/api/register", json={"username": "lin", "password": "secret123"})
    assert register.status_code == 201, register.text
    token = register.json()["token"]

    onboarding = {
        "answers": [
            {"question_number": 1, "question_text": "What do you want more freedom from?", "answer_text": "I want freedom from needing to prove my worth."},
            {"question_number": 2, "question_text": "What feels unresolved right now?", "answer_text": "I feel like I am always slightly outside my own life."},
            {"question_number": 3, "question_text": "What do you notice when you feel most exhausted?", "answer_text": "I shut down and become very private."},
            {"question_number": 4, "question_text": "What part of you feels most neglected?", "answer_text": "My emotional depth and sensitivity."},
            {"question_number": 5, "question_text": "What pattern repeats in your relationships?", "answer_text": "I over-invest and then feel unseen."},
            {"question_number": 6, "question_text": "What do you hope to be different by the end of this season?", "answer_text": "I want to feel more grounded and less like I have to disappear."},
            {"question_number": 7, "question_text": "What has recently happened that bothered you or felt like a calling for you to explore?", "answer_text": "I started saying yes to everyone and lost my center."},
        ]
    }

    save = client.post("/api/onboarding/answers", headers={"Authorization": f"Bearer {token}"}, json=onboarding)
    assert save.status_code == 200, save.text

    hypothesis = client.post(
        "/api/enneagram/hypothesis",
        headers={"Authorization": f"Bearer {token}"},
        json={"answers": onboarding["answers"][:6]},
    )
    assert hypothesis.status_code == 200, hypothesis.text

    profile = client.post(
        "/api/player-profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "values": ["authenticity", "gentleness", "meaning"],
            "fears": ["being unseen", "losing my center", "needing to prove my worth"],
            "desires": ["groundedness", "self-trust", "inner calm"],
            "important_symbols": ["quiet room", "jar of water", "small path"],
            "profile_summary": "A sensitive person learning to trust their own pace and inner steadiness.",
        },
    )
    assert profile.status_code == 200, profile.text

    payload = profile.json()
    assert payload["values"] == ["authenticity", "gentleness", "meaning"]
    assert payload["fears"] == ["being unseen", "losing my center", "needing to prove my worth"]
    assert payload["desires"] == ["groundedness", "self-trust", "inner calm"]
    assert payload["important_symbols"] == ["quiet room", "jar of water", "small path"]
    assert payload["status_labels"]["values"] == "USER_STATED"
    assert payload["status_labels"]["fears"] == "USER_STATED"
    assert payload["status_labels"]["desires"] == "USER_STATED"
    assert payload["status_labels"]["important_symbols"] == "USER_STATED"
    assert payload["status_labels"]["profile_summary"] == "USER_STATED"

    fetched = client.get("/api/player-profile", headers={"Authorization": f"Bearer {token}"})
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["profile_summary"] == payload["profile_summary"]
    assert fetched.json()["status_labels"]["profile_summary"] == "USER_STATED"
