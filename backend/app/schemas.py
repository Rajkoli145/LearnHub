"""Pydantic schemas — request/response validation contracts."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    role: str = "learner"  # learner | instructor


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_verified: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Courses ----------
class CourseCreate(BaseModel):
    title: str
    description: str = ""
    category: str = "General"
    price: float = 0.0
    is_free: bool = True
    thumbnail_url: str = ""


class CourseOut(BaseModel):
    id: int
    instructor_id: int
    title: str
    description: str
    category: str
    price: float
    is_free: bool
    rating_avg: float
    review_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    title: str
    position: int = 0


class LessonCreate(BaseModel):
    title: str
    video_url: str = ""
    content_url: str = ""
    duration: int = 0
    is_free_preview: bool = False
    position: int = 0


class LessonOut(BaseModel):
    id: int
    title: str
    video_url: str
    duration: int
    is_free_preview: bool
    position: int

    class Config:
        from_attributes = True


class SectionOut(BaseModel):
    id: int
    title: str
    position: int
    lessons: List[LessonOut] = []

    class Config:
        from_attributes = True


class QuizSummary(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class CourseDetail(CourseOut):
    sections: List[SectionOut] = []
    quizzes: List[QuizSummary] = []


# ---------- Enrollment ----------
class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    progress: float
    enrolled_at: datetime
    course: Optional[CourseOut] = None

    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    progress: float  # 0..100


# ---------- Quizzes ----------
class QuestionCreate(BaseModel):
    type: str = "mcq"
    prompt: str
    options: List[str] = []
    correct_answer: str
    position: int = 0


class QuizCreate(BaseModel):
    title: str
    pass_mark: int = 60
    max_attempts: int = 3
    questions: List[QuestionCreate] = []


class QuestionOut(BaseModel):
    id: int
    type: str
    prompt: str
    options: List[str] = []
    position: int


class QuizOut(BaseModel):
    id: int
    course_id: int
    title: str
    pass_mark: int
    max_attempts: int
    questions: List[QuestionOut] = []


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str


class QuizSubmit(BaseModel):
    answers: List[AnswerSubmit]


class AttemptResult(BaseModel):
    attempt_id: int
    score: float
    passed: bool
    attempt_number: int
    correct: int
    total: int
