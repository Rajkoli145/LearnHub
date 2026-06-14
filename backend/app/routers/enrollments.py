"""Enrollment module — enroll, list my courses, update progress.

Payment is stubbed: free courses enroll instantly; paid courses simulate a
successful Razorpay checkout (real gateway is Future Scope).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Course, Enrollment, User
from ..schemas import EnrollmentOut, ProgressUpdate

router = APIRouter(prefix="/api/enrollments", tags=["Enrollment"])


@router.post("/{course_id}", response_model=EnrollmentOut, status_code=201)
def enroll(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")

    # Payment gateway stub — paid courses are assumed paid (webhook is future scope).
    enrollment = Enrollment(user_id=user.id, course_id=course_id, progress=0.0)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("", response_model=list[EnrollmentOut])
def my_enrollments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Enrollment).filter(Enrollment.user_id == user.id).all()


@router.patch("/{enrollment_id}/progress", response_model=EnrollmentOut)
def update_progress(
    enrollment_id: int,
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment or enrollment.user_id != user.id:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    enrollment.progress = max(0.0, min(100.0, payload.progress))
    db.commit()
    db.refresh(enrollment)
    return enrollment
