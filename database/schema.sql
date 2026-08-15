-- Inner Garden database schema
-- v0.02
--
-- Sprint 2 introduces the initial persistent tables used by the
-- backend SQLite implementation.

CREATE TABLE IF NOT EXISTS users (
	user_id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	password_hash TEXT,
	created_at TEXT NOT NULL,
	last_login TEXT,
	onboarding_complete INTEGER NOT NULL DEFAULT 0,
	consent_version INTEGER
);

CREATE TABLE IF NOT EXISTS player_profiles (
	profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL UNIQUE,
	profile_summary TEXT,
	created_at TEXT NOT NULL,
	updated_at TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (user_id)
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
