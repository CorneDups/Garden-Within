# Inner Garden

Persistent AI-guided inner-world exploration game.

Current version: **v0.01 — Runnable Inner Garden Shell**

## Sprint 1

This version proves that:

1. the Python/FastAPI backend starts;
2. the browser can load the frontend from the backend;
3. the landing page can enter the Garden;
4. the Garden page loads;
5. `GET /api/health` returns `{"status":"ok"}`.

## Project structure

```text
frontend/
    index.html
    garden.html
    cave.html
    css/
        styles.css
    js/
        main.js

backend/
    __init__.py
    main.py
    requirements.txt

database/
    schema.sql

.env.example
.gitignore
README.md
```

## Run locally

From the repository root:

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Start the application

```bash
uvicorn backend.main:app --reload
```

### 5. Open it

Open:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/api/health
```

FastAPI API docs:

```text
http://127.0.0.1:8000/docs
```

## Sprint 1 acceptance test

- [ ] Backend starts without errors.
- [ ] `/` displays `INNER GARDEN`.
- [ ] Landing page shows a working `Enter` button.
- [ ] Clicking `Enter` loads `/garden`.
- [ ] `/api/health` returns `{"status":"ok"}`.
- [ ] Landing page reports `Garden connection: alive`.
- [ ] Changes are committed to Git.
- [ ] Version tag `v0.01` is created.

## Git / GitHub

After testing:

```bash
git init
git add .
git commit -m "Sprint 1: runnable Inner Garden shell"
git branch -M main
```

Create an empty GitHub repository, then connect it:

```bash
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Tag the tested sprint:

```bash
git tag -a v0.01 -m "Runnable Inner Garden shell"
git push origin v0.01
```

## Next sprint

**Sprint 2 — Persistent Database Connection**

Goal: create a player, restart the backend, and prove that the player still exists.
