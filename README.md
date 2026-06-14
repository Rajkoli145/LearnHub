# LearnHub — Online Learning Platform

> System Design Final Examination Project

LearnHub is an online learning platform where **instructors** publish courses
(sections → lessons → quizzes) and **learners** browse a catalog, enroll, track
progress, and take auto-graded quizzes. The backend is a modular **FastAPI**
service over **SQLAlchemy + SQLite**, with a lightweight **vanilla-JS** frontend.

**GitHub Repository:** `https://github.com/Rajkoli143/LearnHub`
<!-- ↑ Replace with your actual repo URL after pushing. -->

---

## 1. Project Overview

| | |
|---|---|
| **Domain** | E-learning / EdTech |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy ORM |
| **Database** | SQLite (file-based; Postgres-ready) |
| **Auth** | JWT (PyJWT) + PBKDF2 password hashing, role-based access |
| **Frontend** | HTML + CSS + vanilla JavaScript (no build step) |
| **API Docs** | Auto-generated Swagger UI at `/docs` |

### Core Modules (fully implemented)
- **Auth** — register, login, JWT sessions, roles (learner / instructor / admin)
- **Courses** — CRUD for courses, sections, and lessons; public search + filter
- **Enrollment** — enroll, list "My Learning", update lesson progress
- **Quizzes** — instructor authoring, server-side auto-scoring, attempt limits

### Stubbed (documented as Future Scope)
Payments (Razorpay), media/CDN upload, full-text search ranking,
recommendation engine, background task queue, email/OTP service.

---

## 2. Architecture (summary)

```
Browser (vanilla JS SPA)
        │  REST / JSON + JWT
        ▼
FastAPI app  ──►  Routers: auth · courses · enrollments · quizzes
        │
        ▼
SQLAlchemy ORM  ──►  SQLite (learnhub.db)
```

Detailed diagrams are in `learnhubdiagrams/` (architecture, flows, ER models).

---

## 3. Dependencies

Listed in `backend/requirements.txt`:

```
fastapi          # web framework
uvicorn          # ASGI server
SQLAlchemy       # ORM
PyJWT            # JWT auth tokens
pydantic[email]  # request/response validation
```

Password hashing uses Python's standard-library `hashlib` (PBKDF2) — no native
build dependencies.

---

## 4. Setup Instructions

```bash
# 1. Go to the backend
cd backend

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed demo data (creates learnhub.db with sample courses/users/quiz)
python seed.py
```

---

## 5. Execution Steps

```bash
# From the backend/ directory, with the venv active:
uvicorn app.main:app --reload
```

Then open:

| URL | What |
|---|---|
| http://127.0.0.1:8000/ | **Web app** (frontend) |
| http://127.0.0.1:8000/docs | **Swagger API docs** (interactive) |
| http://127.0.0.1:8000/api/health | Health check |

### Demo accounts (password: `Passw0rd!`)
| Email | Role |
|---|---|
| `learner@learnhub.dev` | learner (pre-enrolled in a course) |
| `instructor@learnhub.dev` | instructor (owns the sample courses) |
| `admin@learnhub.dev` | admin |

### Try it
1. Open `/` → browse the **Course Catalog**.
2. **Login** as the learner → **My Learning** shows progress.
3. Open *Python for Beginners* → **Take Quiz** → submit → see auto-graded score.
4. Login as the **instructor** → **+ Course** to create one, **+ Add Quiz** to author questions.

---

## 6. API Reference (main endpoints)

| Method | Path | Module | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Auth | — |
| POST | `/api/auth/login` | Auth | — |
| GET | `/api/auth/me` | Auth | JWT |
| GET | `/api/courses?q=&category=` | Courses | — |
| GET | `/api/courses/{id}` | Courses | — |
| POST | `/api/courses` | Courses | instructor/admin |
| POST | `/api/courses/{id}/sections` | Courses | owner |
| POST | `/api/courses/sections/{id}/lessons` | Courses | owner |
| POST | `/api/enrollments/{course_id}` | Enrollment | JWT |
| GET | `/api/enrollments` | Enrollment | JWT |
| PATCH | `/api/enrollments/{id}/progress` | Enrollment | JWT |
| POST | `/api/courses/{id}/quizzes` | Quizzes | owner |
| GET | `/api/quizzes/{id}` | Quizzes | JWT |
| POST | `/api/quizzes/{id}/submit` | Quizzes | JWT |

---

## 7. Project Structure

```
LearnHub/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, router wiring, static serving
│   │   ├── database.py      # engine, session, Base
│   │   ├── models.py        # SQLAlchemy ORM models (10 tables)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── auth.py          # password hashing + JWT + role guards
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── courses.py
│   │       ├── enrollments.py
│   │       └── quizzes.py
│   ├── seed.py              # demo data loader
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js               # vanilla-JS SPA
├── learnhubdiagrams/        # architecture, flow & ER diagrams
└── README.md
```

---

## 8. Future Scope
- Razorpay payment gateway + webhook-confirmed paid enrollment
- Media uploads to S3/CDN with presigned URLs and video streaming
- PostgreSQL + Alembic migrations; full-text search (`tsvector`) with ranking
- ML recommendation engine (scikit-learn) and personalized course feed
- Celery task queue for emails, certificate generation, analytics
- Email / OTP verification and password reset
