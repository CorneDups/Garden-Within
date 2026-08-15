import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DEFAULT_DATABASE_PATH = BASE_DIR / "database" / "inner_garden.db"
DEFAULT_SECRET_KEY = "inner-garden-dev-secret-change-me"
DATABASE_PATH = Path(os.environ.get("INNER_GARDEN_DB_PATH", DEFAULT_DATABASE_PATH))
SECRET_KEY = os.environ.get("INNER_GARDEN_SECRET_KEY", DEFAULT_SECRET_KEY)
ACTIVE_SESSIONS: dict[str, dict[str, Any]] = {}


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password_hash: str | None = Field(default=None, max_length=255)


class UserRecord(BaseModel):
    user_id: int
    username: str
    password_hash: str | None
    created_at: str
    last_login: str | None
    onboarding_complete: bool
    consent_version: int | None


def configure_database_path(path: str | Path) -> Path:
    global DATABASE_PATH
    DATABASE_PATH = Path(path)
    return DATABASE_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash or not password_hash.startswith("pbkdf2_sha256$"):
        return False

    _, salt, digest_hex = password_hash.split("$", 2)
    expected = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return hmac.compare_digest(expected.hex(), digest_hex)


def initialize_database() -> None:
    database_path = Path(DATABASE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT,
                onboarding_complete INTEGER NOT NULL DEFAULT 0,
                consent_version INTEGER
            );

            CREATE TABLE IF NOT EXISTS game_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS onboarding_answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_number INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS enneagram_hypotheses (
                hypothesis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                primary_type INTEGER NOT NULL,
                wing INTEGER NOT NULL,
                confidence REAL NOT NULL,
                type_probabilities TEXT NOT NULL,
                reasoning_summary TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS player_profiles (
                profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                values_json TEXT NOT NULL DEFAULT '[]',
                fears_json TEXT NOT NULL DEFAULT '[]',
                desires_json TEXT NOT NULL DEFAULT '[]',
                important_symbols_json TEXT NOT NULL DEFAULT '[]',
                profile_summary TEXT NOT NULL DEFAULT '',
                status_labels_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
            """
        )

        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(player_profiles)").fetchall()
        }
        for column_name, definition in {
            "values_json": "TEXT NOT NULL DEFAULT '[]'",
            "fears_json": "TEXT NOT NULL DEFAULT '[]'",
            "desires_json": "TEXT NOT NULL DEFAULT '[]'",
            "important_symbols_json": "TEXT NOT NULL DEFAULT '[]'",
            "status_labels_json": "TEXT NOT NULL DEFAULT '{}'",
        }.items():
            if column_name not in existing_columns:
                connection.execute(f"ALTER TABLE player_profiles ADD COLUMN {column_name} {definition}")


def row_to_user(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "created_at": row["created_at"],
        "last_login": row["last_login"],
        "onboarding_complete": bool(row["onboarding_complete"]),
        "consent_version": row["consent_version"],
    }


def create_session_token(user_id: int, username: str) -> str:
    token = secrets.token_urlsafe(32)
    ACTIVE_SESSIONS[token] = {"user_id": user_id, "username": username}
    return token


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid bearer token.")

    return authorization.split(" ", 1)[1].strip()


def require_auth(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = get_bearer_token(authorization)
    session = ACTIVE_SESSIONS.get(token)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session.")

    return session

app = FastAPI(
    title="Inner Garden API",
    version="0.02",
    description="Backend prototype for the Inner Garden project.",
)

app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js",
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/garden", include_in_schema=False)
async def garden() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "garden.html")


@app.get("/cave", include_in_schema=False)
async def cave() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "cave.html")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/users", response_model=UserRecord, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> dict[str, Any]:
    created_at = utc_now()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, password_hash, created_at, last_login, onboarding_complete, consent_version)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (payload.username, payload.password_hash, created_at, None, 0, None),
            )
            user_id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.") from exc

    if row is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User record was not created.")

    return row_to_user(row)


@app.get("/api/users/{user_id}", response_model=UserRecord)
async def get_user(user_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return row_to_user(row)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=255)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=255)


class OnboardingAnswer(BaseModel):
    question_number: int = Field(ge=1, le=7)
    question_text: str = Field(min_length=1, max_length=2000)
    answer_text: str = Field(min_length=1, max_length=20000)


class OnboardingAnswerSet(BaseModel):
    answers: list[OnboardingAnswer]


class PlayerProfileRequest(BaseModel):
    values: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    desires: list[str] = Field(default_factory=list)
    important_symbols: list[str] = Field(default_factory=list)
    profile_summary: str = Field(default="", max_length=4000)


class EnneagramHypothesisRequest(BaseModel):
    answers: list[OnboardingAnswer]


ONBOARDING_QUESTIONS = [
    "What do you want more freedom from?",
    "What feels unresolved right now?",
    "What do you notice when you feel most exhausted?",
    "What part of you feels most neglected?",
    "What pattern repeats in your relationships?",
    "What do you hope to be different by the end of this season?",
    "What has recently happened that bothered you or felt like a calling for you to explore? Give as much detail as you feel comfortable with.",
]

TYPE_KEYWORDS = {
    1: ["should", "responsibility", "order", "rules", "standards", "perfection", "duty", "wrong", "right", "discipline", "rigid", "control"],
    2: ["help", "care", "support", "connection", "love", "needed", "people", "giving", "approve", "service", "nurture", "useful"],
    3: ["success", "achievement", "image", "ambition", "performance", "winning", "career", "status", "recognition", "productive", "competitive"],
    4: ["identity", "difference", "deep", "sensitive", "authentic", "meaning", "unique", "alone", "creative", "emotional", "profound"],
    5: ["understand", "knowledge", "analysis", "private", "quiet", "curious", "information", "detached", "expert", "research", "observe"],
    6: ["security", "anxiety", "doubt", "trust", "loyalty", "support", "fear", "prepare", "responsible", "reassurance", "safety"],
    7: ["freedom", "possibility", "wonder", "adventure", "fun", "options", "curiosity", "open", "expand", "escape", "limitless"],
    8: ["power", "control", "strength", "boundaries", "conflict", "force", "assertive", "protect", "independence", "dominance"],
    9: ["peace", "harmony", "calm", "acceptance", "comfort", "merge", "balance", "easy", "rest", "avoidance", "gentle"],
}

MOCK_PERSONALITY_PROFILES = {
    "analyst": {1: 1.0, 2: 0.7, 3: 0.8, 4: 1.3, 5: 1.4, 6: 0.9, 7: 1.0, 8: 0.6, 9: 0.7},
    "guardian": {1: 1.3, 2: 1.1, 3: 0.7, 4: 1.0, 5: 0.7, 6: 1.4, 7: 0.8, 8: 1.2, 9: 0.9},
    "poet": {1: 0.7, 2: 1.0, 3: 0.8, 4: 1.6, 5: 1.0, 6: 1.0, 7: 1.2, 8: 0.7, 9: 1.1},
}


def select_mock_personality(user_id: int) -> str:
    return ["analyst", "guardian", "poet"][user_id % 3]


def generate_enneagram_hypothesis(user_id: int, answers: list[OnboardingAnswer]) -> dict[str, Any]:
    if not answers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one answer is required.")

    personality = select_mock_personality(user_id)
    weights = MOCK_PERSONALITY_PROFILES[personality]
    totals = {str(type_number): 0.0 for type_number in range(1, 10)}

    for answer in answers:
        text = answer.answer_text.lower()
        for type_number, keywords in TYPE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score:
                totals[str(type_number)] += score * weights[type_number]

    if all(value == 0 for value in totals.values()):
        totals = {"4": 4.0, "5": 3.0, "6": 2.0, "1": 1.0, "2": 1.0, "3": 1.0, "7": 1.0, "8": 1.0, "9": 1.0}

    total_weight = sum(totals.values())
    if total_weight == 0:
        total_weight = 1.0

    type_probabilities = {key: float(value) / total_weight for key, value in totals.items()}
    primary_type = max(totals, key=lambda key: totals[key])
    primary_int = int(primary_type)

    wing_candidates = [
        ((primary_int - 1) if primary_int > 1 else 9),
        ((primary_int + 1) if primary_int < 9 else 1),
        primary_int,
    ]
    wing = max(wing_candidates, key=lambda candidate: totals[str(candidate)])

    confidence = min(0.99, max(0.25, (totals[str(primary_int)] / total_weight) + 0.35))
    reasoning_summary = (
        f"Mock {personality} analysis suggests a strong {primary_int} profile with a {wing} wing, "
        f"reflecting recurring themes of identity, meaning, and self-trust."
    )

    return {
        "primary_type": primary_int,
        "wing": int(wing),
        "confidence": round(float(confidence), 3),
        "type_probabilities": {key: round(float(value), 4) for key, value in sorted(type_probabilities.items(), key=lambda item: int(item[0]))},
        "reasoning_summary": reasoning_summary,
    }


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest) -> dict[str, Any]:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE username = ?", (request.username,)).fetchone()
        if row is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")

        password_hash = hash_password(request.password)
        cursor = connection.execute(
            """
            INSERT INTO users (username, password_hash, created_at, last_login, onboarding_complete, consent_version)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (request.username, password_hash, utc_now(), None, 0, None),
        )
        user_id = cursor.lastrowid

    token = create_session_token(user_id, request.username)
    return {"user_id": user_id, "username": request.username, "token": token}


@app.post("/api/login")
async def login(request: LoginRequest) -> dict[str, Any]:
    with get_connection() as connection:
        user_row = connection.execute("SELECT * FROM users WHERE username = ?", (request.username,)).fetchone()

    if user_row is None or not verify_password(request.password, user_row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    token = create_session_token(user_row["user_id"], user_row["username"])
    with get_connection() as connection:
        connection.execute(
            "UPDATE users SET last_login = ? WHERE user_id = ?",
            (utc_now(), user_row["user_id"]),
        )

    return {"user_id": user_row["user_id"], "username": user_row["username"], "token": token}


@app.post("/api/logout")
async def logout(authorization: str | None = Header(default=None)) -> dict[str, str]:
    token = get_bearer_token(authorization)
    ACTIVE_SESSIONS.pop(token, None)
    return {"status": "logged_out"}


@app.get("/api/me")
async def me(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    session = require_auth(authorization)
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "onboarding_complete": bool(row["onboarding_complete"]),
        "consent_version": row["consent_version"],
    }


@app.get("/api/onboarding/questions")
async def get_onboarding_questions(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    session = require_auth(authorization)
    with get_connection() as connection:
        row = connection.execute("SELECT onboarding_complete FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if bool(row["onboarding_complete"]):
        return {"questions": []}

    return {"questions": [{"question_number": index, "question": question} for index, question in enumerate(ONBOARDING_QUESTIONS, start=1)]}


@app.post("/api/onboarding/answers")
async def save_onboarding_answers(payload: OnboardingAnswerSet, authorization: str | None = Header(default=None)) -> dict[str, str]:
    session = require_auth(authorization)
    if len(payload.answers) not in {6, 7}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exactly six or seven answers are required.")

    with get_connection() as connection:
        existing = connection.execute("SELECT onboarding_complete FROM users WHERE user_id = ?", (session["user_id"],)).fetchone()
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if bool(existing["onboarding_complete"]) and len(payload.answers) == 7:
            return {"status": "saved"}

        for answer in payload.answers:
            connection.execute(
                "INSERT INTO onboarding_answers (user_id, question_number, question_text, answer_text, created_at) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], answer.question_number, answer.question_text, answer.answer_text, utc_now()),
            )

        if len(payload.answers) == 7:
            connection.execute(
                "UPDATE users SET onboarding_complete = 1 WHERE user_id = ?",
                (session["user_id"],),
            )

    return {"status": "saved"}


@app.post("/api/enneagram/hypothesis")
async def create_hypothesis(payload: EnneagramHypothesisRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    session = require_auth(authorization)
    if not payload.answers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one answer is required.")

    result = generate_enneagram_hypothesis(session["user_id"], payload.answers)
    created_at = utc_now()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO enneagram_hypotheses (user_id, primary_type, wing, confidence, type_probabilities, reasoning_summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                result["primary_type"],
                result["wing"],
                result["confidence"],
                str(result["type_probabilities"]),
                result["reasoning_summary"],
                created_at,
                created_at,
            ),
        )

    return result


@app.get("/api/enneagram/hypothesis")
async def get_hypothesis(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    session = require_auth(authorization)
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM enneagram_hypotheses WHERE user_id = ? ORDER BY hypothesis_id DESC LIMIT 1",
            (session["user_id"],),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hypothesis found for this user.")

    return {
        "primary_type": row["primary_type"],
        "wing": row["wing"],
        "confidence": row["confidence"],
        "type_probabilities": eval(row["type_probabilities"], {"__builtins__": {}}, {}),
        "reasoning_summary": row["reasoning_summary"],
    }


@app.post("/api/player-profile")
async def save_player_profile(payload: PlayerProfileRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    session = require_auth(authorization)
    now = utc_now()
    status_labels = {
        "values": "USER_STATED",
        "fears": "USER_STATED",
        "desires": "USER_STATED",
        "important_symbols": "USER_STATED",
        "profile_summary": "USER_STATED",
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO player_profiles (
                user_id,
                values_json,
                fears_json,
                desires_json,
                important_symbols_json,
                profile_summary,
                status_labels_json,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                values_json = excluded.values_json,
                fears_json = excluded.fears_json,
                desires_json = excluded.desires_json,
                important_symbols_json = excluded.important_symbols_json,
                profile_summary = excluded.profile_summary,
                status_labels_json = excluded.status_labels_json,
                updated_at = excluded.updated_at
            """,
            (
                session["user_id"],
                str(payload.values),
                str(payload.fears),
                str(payload.desires),
                str(payload.important_symbols),
                payload.profile_summary,
                str(status_labels),
                now,
                now,
            ),
        )

    return {
        "values": payload.values,
        "fears": payload.fears,
        "desires": payload.desires,
        "important_symbols": payload.important_symbols,
        "profile_summary": payload.profile_summary,
        "status_labels": status_labels,
    }


@app.get("/api/player-profile")
async def get_player_profile(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    session = require_auth(authorization)
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM player_profiles WHERE user_id = ?", (session["user_id"],)).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No player profile found for this user.")

    return {
        "values": eval(row["values_json"], {"__builtins__": {}}, {}),
        "fears": eval(row["fears_json"], {"__builtins__": {}}, {}),
        "desires": eval(row["desires_json"], {"__builtins__": {}}, {}),
        "important_symbols": eval(row["important_symbols_json"], {"__builtins__": {}}, {}),
        "profile_summary": row["profile_summary"],
        "status_labels": eval(row["status_labels_json"], {"__builtins__": {}}, {}),
    }


initialize_database()
