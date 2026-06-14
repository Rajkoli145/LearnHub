"""Seed the database with demo data for screenshots / grading.

Run from the backend/ directory:  python seed.py
Idempotent — wipes and recreates the demo rows each run.

Demo logins (password for all):  Passw0rd!
  instructor@learnhub.dev   (instructor)
  learner@learnhub.dev      (learner)
  admin@learnhub.dev        (admin)
"""
import json

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import (
    Course,
    Enrollment,
    Lesson,
    Question,
    Quiz,
    Section,
    User,
)

DEMO_PASSWORD = "Passw0rd!"


def run():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    pw = hash_password(DEMO_PASSWORD)
    instructor = User(email="instructor@learnhub.dev", password_hash=pw,
                      full_name="Asha Mentor", role="instructor", is_verified=True)
    learner = User(email="learner@learnhub.dev", password_hash=pw,
                   full_name="Ravi Student", role="learner", is_verified=True)
    admin = User(email="admin@learnhub.dev", password_hash=pw,
                 full_name="Site Admin", role="admin", is_verified=True)
    db.add_all([instructor, learner, admin])
    db.flush()

    courses = [
        Course(instructor_id=instructor.id, title="Python for Beginners",
               description="Learn Python from zero — variables, loops, functions, projects.",
               category="Programming", price=0.0, is_free=True,
               rating_avg=4.6, review_count=120),
        Course(instructor_id=instructor.id, title="System Design Fundamentals",
               description="Scalable architecture, databases, caching, queues, load balancing.",
               category="Engineering", price=499.0, is_free=False,
               rating_avg=4.8, review_count=87),
        Course(instructor_id=instructor.id, title="Web Dev with FastAPI",
               description="Build REST APIs, auth, and databases using FastAPI + SQLAlchemy.",
               category="Web", price=299.0, is_free=False,
               rating_avg=4.7, review_count=64),
    ]
    db.add_all(courses)
    db.flush()

    # Curriculum for the first course.
    py = courses[0]
    sec1 = Section(course_id=py.id, title="Getting Started", position=1)
    sec2 = Section(course_id=py.id, title="Core Concepts", position=2)
    db.add_all([sec1, sec2])
    db.flush()
    db.add_all([
        Lesson(section_id=sec1.id, title="Installing Python", duration=420,
               is_free_preview=True, position=1, video_url="https://example.com/v/1"),
        Lesson(section_id=sec1.id, title="Your First Program", duration=600,
               position=2, video_url="https://example.com/v/2"),
        Lesson(section_id=sec2.id, title="Variables & Types", duration=540,
               position=1, video_url="https://example.com/v/3"),
        Lesson(section_id=sec2.id, title="Loops & Functions", duration=720,
               position=2, video_url="https://example.com/v/4"),
    ])

    # Quiz for the first course.
    quiz = Quiz(course_id=py.id, title="Python Basics Quiz", pass_mark=60, max_attempts=3)
    db.add(quiz)
    db.flush()
    db.add_all([
        Question(quiz_id=quiz.id, type="mcq", prompt="Which keyword defines a function?",
                 options=json.dumps(["func", "def", "function", "lambda"]),
                 correct_answer="def", position=1),
        Question(quiz_id=quiz.id, type="mcq", prompt="What is the output of print(2 ** 3)?",
                 options=json.dumps(["6", "8", "9", "5"]),
                 correct_answer="8", position=2),
        Question(quiz_id=quiz.id, type="boolean", prompt="Python is case-sensitive.",
                 options=json.dumps(["true", "false"]),
                 correct_answer="true", position=3),
    ])

    # Learner already enrolled in the free course.
    db.add(Enrollment(user_id=learner.id, course_id=py.id, progress=50.0))

    db.commit()
    db.close()
    print("Seed complete.")
    print(f"  Demo password for all accounts: {DEMO_PASSWORD}")
    print("  instructor@learnhub.dev / learner@learnhub.dev / admin@learnhub.dev")


if __name__ == "__main__":
    run()
