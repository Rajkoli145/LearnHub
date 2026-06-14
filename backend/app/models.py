"""SQLAlchemy ORM models — mirrors the LearnHub ER diagrams.

Tables: users, courses, sections, lessons, resources, enrollments,
quizzes, questions, quiz_attempts, attempt_answers.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False, default="")
    role = Column(String, nullable=False, default="learner")  # learner | instructor | admin
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)

    courses = relationship("Course", back_populates="instructor", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="General")
    thumbnail_url = Column(String, default="")
    preview_video_url = Column(String, default="")
    price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=True)
    rating_avg = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    instructor = relationship("User", back_populates="courses")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    course = relationship("Course", back_populates="sections")
    lessons = relationship("Lesson", back_populates="section", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    title = Column(String, nullable=False)
    video_url = Column(String, default="")
    content_url = Column(String, default="")
    duration = Column(Integer, default=0)  # seconds
    is_free_preview = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    section = relationship("Section", back_populates="lessons")
    resources = relationship("Resource", back_populates="lesson", cascade="all, delete-orphan")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, default="")
    type = Column(String, default="pdf")  # pdf | code | link
    created_at = Column(DateTime, default=_now)

    lesson = relationship("Lesson", back_populates="resources")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress = Column(Float, default=0.0)  # 0..100 percent
    enrolled_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    attempts = relationship("QuizAttempt", back_populates="enrollment", cascade="all, delete-orphan")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    pass_mark = Column(Integer, default=60)  # percent needed to pass
    max_attempts = Column(Integer, default=3)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)

    course = relationship("Course", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    type = Column(String, default="mcq")  # mcq | boolean
    prompt = Column(Text, nullable=False)
    options = Column(Text, default="[]")  # JSON-encoded list of choices
    correct_answer = Column(String, nullable=False)
    position = Column(Integer, default=0)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    attempt_number = Column(Integer, default=1)
    submitted_at = Column(DateTime, default=_now)

    enrollment = relationship("Enrollment", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_given = Column(String, default="")
    is_correct = Column(Boolean, default=False)

    attempt = relationship("QuizAttempt", back_populates="answers")
