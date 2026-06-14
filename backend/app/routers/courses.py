"""Courses module — CRUD for courses, sections, lessons.

Public browse/detail endpoints; create/edit restricted to the owning
instructor (or admin). Mirrors the Course module diagram.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_role
from ..database import get_db
from ..models import Course, Lesson, Section, User
from ..schemas import (
    CourseCreate,
    CourseDetail,
    CourseOut,
    LessonCreate,
    LessonOut,
    SectionCreate,
    SectionOut,
)

router = APIRouter(prefix="/api/courses", tags=["Courses"])


def _owner_or_admin(course: Course, user: User):
    if user.role != "admin" and course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Not the course owner")


@router.get("", response_model=list[CourseOut])
def list_courses(
    q: str | None = Query(None, description="search title/description"),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Public course browser with basic search + category filter."""
    query = db.query(Course)
    if q:
        like = f"%{q}%"
        query = query.filter(Course.title.ilike(like) | Course.description.ilike(like))
    if category:
        query = query.filter(Course.category == category)
    return query.order_by(Course.created_at.desc()).all()


@router.get("/{course_id}", response_model=CourseDetail)
def course_detail(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("", response_model=CourseOut, status_code=201)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("instructor", "admin")),
):
    course = Course(instructor_id=user.id, **payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.post("/{course_id}/sections", response_model=SectionOut, status_code=201)
def add_section(
    course_id: int,
    payload: SectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    _owner_or_admin(course, user)
    section = Section(course_id=course_id, **payload.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


@router.post("/sections/{section_id}/lessons", response_model=LessonOut, status_code=201)
def add_lesson(
    section_id: int,
    payload: LessonCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    _owner_or_admin(section.course, user)
    lesson = Lesson(section_id=section_id, **payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    _owner_or_admin(course, user)
    db.delete(course)
    db.commit()
