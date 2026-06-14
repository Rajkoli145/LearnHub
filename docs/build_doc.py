"""Build the LearnHub project documentation as a self-contained HTML file.

Embeds screenshots as base64 so the file (and the PDF printed from it) needs
no external assets. Run:  python build_doc.py  →  Documentation.html
Then print to PDF with Chrome --headless --print-to-pdf.
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def b64(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


IMG_CATALOG = b64("lh_catalog.png")
IMG_LOGIN = b64("lh_login.png")
IMG_DOCS = b64("lh_docs.png")

HTML = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>LearnHub — Project Documentation</title>
<style>
  @page {{ size: A4; margin: 18mm 16mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a2e; line-height: 1.5; font-size: 12.5px; }}
  h1 {{ font-size: 30px; margin: 0; }}
  h2 {{ font-size: 19px; border-bottom: 2px solid #5b8cff; padding-bottom: 4px; margin-top: 26px; color: #21305b; }}
  h3 {{ font-size: 15px; color: #21305b; margin-bottom: 4px; }}
  .cover {{ text-align: center; padding: 120px 0 80px; }}
  .cover .sub {{ color: #5b8cff; font-size: 18px; margin-top: 8px; }}
  .cover .meta {{ margin-top: 60px; color: #555; font-size: 14px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 11.5px; }}
  th, td {{ border: 1px solid #cbd2e8; padding: 6px 9px; text-align: left; vertical-align: top; }}
  th {{ background: #eef2fb; }}
  code {{ background: #eef2fb; padding: 1px 5px; border-radius: 4px; font-size: 11px; }}
  pre {{ background: #1a1f33; color: #e8eaf5; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 11px; }}
  .pagebreak {{ page-break-before: always; }}
  figure {{ margin: 12px 0; text-align: center; }}
  figure img {{ max-width: 100%; border: 1px solid #cbd2e8; border-radius: 8px; }}
  figcaption {{ color: #666; font-size: 11px; margin-top: 4px; }}
  ul {{ margin: 6px 0; }}
</style></head><body>

<div class="cover">
  <h1>🎓 LearnHub</h1>
  <div class="sub">Online Learning Platform</div>
  <p style="margin-top:30px; font-size:15px; color:#444;">System Design — Final Examination Project Documentation</p>
  <div class="meta">
    <p><b>Submitted by:</b> ______________________</p>
    <p><b>Roll No:</b> ______________________</p>
    <p><b>Course:</b> System Design</p>
    <p><b>Date:</b> June 2026</p>
  </div>
</div>

<div class="pagebreak"></div>

<h2>1. Problem Statement</h2>
<p>Learners lack a single, structured platform to discover quality courses, enroll,
follow an organized curriculum, and validate their understanding through assessments.
Instructors lack a simple way to publish structured course content and measure learner
performance. A scalable system is needed that cleanly separates concerns — authentication,
course management, enrollment, and assessment — so each can evolve and scale independently.</p>

<h2>2. Proposed Solution</h2>
<p>LearnHub is a modular web platform built on a <b>FastAPI</b> backend exposing a REST API,
backed by a relational database via the <b>SQLAlchemy</b> ORM, with a lightweight JavaScript
frontend. Functionality is split into four independent modules:</p>
<ul>
  <li><b>Auth</b> — JWT-based authentication with role-based access (learner, instructor, admin).</li>
  <li><b>Courses</b> — instructors create courses organized into sections and lessons; learners browse, search, and filter.</li>
  <li><b>Enrollment</b> — learners enroll in courses and track lesson-level progress.</li>
  <li><b>Quizzes</b> — instructors author quizzes; the server auto-grades submissions and enforces attempt limits.</li>
</ul>
<p>The modular router design mirrors a microservice-style separation while remaining a single
deployable app — each module can later be extracted into its own service.</p>

<h2>3. System Architecture</h2>
<pre>
 ┌────────────────────────────┐
 │   Browser (vanilla-JS SPA) │
 └─────────────┬──────────────┘
               │  REST / JSON  +  JWT (Bearer)
               ▼
 ┌────────────────────────────────────────────┐
 │              FastAPI Application            │
 │  ┌──────┬─────────┬────────────┬─────────┐ │
 │  │ Auth │ Courses │ Enrollment │ Quizzes │ │  ← routers
 │  └──────┴─────────┴────────────┴─────────┘ │
 │   JWT auth · role guards · validation      │
 └─────────────────────┬──────────────────────┘
                       │  SQLAlchemy ORM
                       ▼
 ┌────────────────────────────┐
 │  SQLite  (learnhub.db)     │   ← Postgres-ready
 └────────────────────────────┘
</pre>
<p>Request flow: the client sends JSON with a JWT in the <code>Authorization</code> header →
FastAPI validates the token and the request body (Pydantic) → the matching router enforces
role/ownership rules → SQLAlchemy reads/writes the database → a validated JSON response is returned.
Detailed architecture, sequence, and ER diagrams are maintained in the <code>learnhubdiagrams/</code> folder.</p>

<div class="pagebreak"></div>
<h2>4. Module Description</h2>
<table>
  <tr><th>Module</th><th>Responsibility</th><th>Key Endpoints</th></tr>
  <tr><td><b>Auth</b></td><td>Registration, login, JWT issuance, role enforcement, password hashing (PBKDF2).</td>
      <td>POST /api/auth/register<br>POST /api/auth/login<br>GET /api/auth/me</td></tr>
  <tr><td><b>Courses</b></td><td>Course/section/lesson CRUD, public catalog with search &amp; category filter, ownership checks.</td>
      <td>GET /api/courses<br>GET /api/courses/{{id}}<br>POST /api/courses</td></tr>
  <tr><td><b>Enrollment</b></td><td>Enroll learners, list "My Learning", update progress percentage.</td>
      <td>POST /api/enrollments/{{cid}}<br>GET /api/enrollments<br>PATCH …/progress</td></tr>
  <tr><td><b>Quizzes</b></td><td>Author quizzes/questions, serve quizzes without leaking answers, auto-grade, enforce max attempts.</td>
      <td>POST /api/courses/{{id}}/quizzes<br>GET /api/quizzes/{{id}}<br>POST /api/quizzes/{{id}}/submit</td></tr>
</table>

<h2>5. Database Design</h2>
<p>Ten relational tables model the domain. Primary relationships:</p>
<ul>
  <li><code>users</code> 1—N <code>courses</code> (an instructor owns many courses)</li>
  <li><code>courses</code> 1—N <code>sections</code> 1—N <code>lessons</code> 1—N <code>resources</code></li>
  <li><code>users</code> N—N <code>courses</code> via <code>enrollments</code></li>
  <li><code>courses</code> 1—N <code>quizzes</code> 1—N <code>questions</code></li>
  <li><code>quiz_attempts</code> 1—N <code>attempt_answers</code> (one row per answered question)</li>
</ul>
<table>
  <tr><th>Table</th><th>Important Columns</th></tr>
  <tr><td>users</td><td>id, email (unique), password_hash, full_name, role, is_verified, created_at</td></tr>
  <tr><td>courses</td><td>id, instructor_id (FK), title, description, category, price, is_free, rating_avg, review_count</td></tr>
  <tr><td>sections</td><td>id, course_id (FK), title, position</td></tr>
  <tr><td>lessons</td><td>id, section_id (FK), title, video_url, duration, is_free_preview, position</td></tr>
  <tr><td>resources</td><td>id, lesson_id (FK), title, url, type</td></tr>
  <tr><td>enrollments</td><td>id, user_id (FK), course_id (FK), progress, enrolled_at</td></tr>
  <tr><td>quizzes</td><td>id, course_id (FK), title, pass_mark, max_attempts, order_index</td></tr>
  <tr><td>questions</td><td>id, quiz_id (FK), type, prompt, options (JSON), correct_answer, position</td></tr>
  <tr><td>quiz_attempts</td><td>id, quiz_id (FK), enrollment_id (FK), user_id (FK), score, passed, attempt_number</td></tr>
  <tr><td>attempt_answers</td><td>id, attempt_id (FK), question_id (FK), answer_given, is_correct</td></tr>
</table>

<h2>6. Technology Stack</h2>
<table>
  <tr><th>Layer</th><th>Technology</th><th>Why</th></tr>
  <tr><td>Language</td><td>Python 3.11+</td><td>Required; rich ecosystem</td></tr>
  <tr><td>API framework</td><td>FastAPI</td><td>Async, auto OpenAPI docs, Pydantic validation</td></tr>
  <tr><td>ORM</td><td>SQLAlchemy 2.0</td><td>DB-agnostic models; easy SQLite→Postgres</td></tr>
  <tr><td>Database</td><td>SQLite</td><td>Zero-setup; file-based; production swaps to PostgreSQL</td></tr>
  <tr><td>Auth</td><td>PyJWT + hashlib PBKDF2</td><td>Stateless tokens; no native build deps</td></tr>
  <tr><td>Server</td><td>Uvicorn (ASGI)</td><td>Fast async server</td></tr>
  <tr><td>Frontend</td><td>HTML/CSS/JS</td><td>No build step; easy to run and demo</td></tr>
</table>

<div class="pagebreak"></div>
<h2>7. Implementation Details</h2>
<p><b>Authentication.</b> Passwords are hashed with PBKDF2-HMAC-SHA256 (200k iterations,
per-user salt) using the standard library. On login the server issues a JWT carrying the user id
and a 24-hour expiry. Protected routes depend on <code>get_current_user</code>; role-restricted
routes use a <code>require_role(...)</code> dependency factory.</p>
<p><b>Quiz auto-grading.</b> The quiz-fetch endpoint deliberately strips
<code>correct_answer</code> so it can never be read from the browser. On submit, the server
compares each answer case-insensitively, computes a percentage score, marks the attempt
passed/failed against the quiz <code>pass_mark</code>, and persists every answer for review.
<code>max_attempts</code> is enforced server-side.</p>
<p><b>Validation &amp; safety.</b> Every request/response is typed with Pydantic schemas, giving
automatic 422 errors on bad input and a self-documenting OpenAPI spec. Ownership checks prevent
one instructor from editing another's course.</p>
<pre>POST /api/quizzes/1/submit          # all-correct submission
→ {{ "score": 100.0, "passed": true, "correct": 3, "total": 3, "attempt_number": 1 }}

POST /api/courses   (as learner)    # role guard blocks non-instructors
→ 403  {{ "detail": "Requires role: instructor, admin" }}</pre>

<h2>8. Screenshots</h2>
<figure><img src="{IMG_CATALOG}"><figcaption>Course catalog — search, ratings, free/paid badges.</figcaption></figure>
<figure><img src="{IMG_LOGIN}"><figcaption>Login screen with demo accounts.</figcaption></figure>
<figure><img src="{IMG_DOCS}"><figcaption>Auto-generated Swagger API documentation at /docs.</figcaption></figure>
<p class="figcaption" style="color:#666;font-size:11px;">Additional screens (My Learning dashboard, quiz attempt &amp; result) can be captured
after logging in locally with the demo accounts.</p>

<h2>9. Future Scope</h2>
<ul>
  <li>Razorpay payment gateway with webhook-confirmed paid enrollment.</li>
  <li>Media uploads to S3/CDN with presigned URLs and video streaming.</li>
  <li>Migration to PostgreSQL with Alembic migrations; full-text search ranking.</li>
  <li>ML-based recommendation engine (scikit-learn) for a personalized feed.</li>
  <li>Celery task queue for emails, certificate generation, and analytics.</li>
  <li>Email/OTP verification, password reset, and instructor payout management.</li>
</ul>

</body></html>"""

out = os.path.join(HERE, "Documentation.html")
with open(out, "w") as f:
    f.write(HTML)
print("Wrote", out)
