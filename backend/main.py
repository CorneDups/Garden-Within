from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Inner Garden API",
    version="0.01",
    description="Backend shell for the Inner Garden prototype.",
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
