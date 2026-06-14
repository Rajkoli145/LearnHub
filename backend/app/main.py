"""LearnHub API — FastAPI application entrypoint.

Wires the core modules (Auth, Courses, Enrollment, Quizzes), creates the
SQLite schema on startup, and serves the static frontend.

Run:  uvicorn app.main:app --reload   (from the backend/ directory)
Docs: http://127.0.0.1:8000/docs
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import auth, courses, enrollments, quizzes

# Create tables on startup (Alembic migrations are Future Scope).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LearnHub API",
    description="Online learning platform — System Design final project.",
    version="1.0.0",
)

# CORS open for local dev / demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(quizzes.router)


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "LearnHub API"}


# ---------- Serve the static frontend ----------
_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(_FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    def root():
        return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))
