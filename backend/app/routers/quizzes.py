"""Quiz module — create quiz, fetch (without answers), submit + auto-score.

Scoring runs server-side. Correct answers are never sent to the client in
the fetch endpoint, so the quiz can't be cheated from the browser.
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import (
    AttemptAnswer,
    Course,
    Enrollment,
    Question,
    Quiz,
    QuizAttempt,
    User,
)
from ..schemas import AttemptResult, QuestionOut, QuizCreate, QuizOut, QuizSubmit

router = APIRouter(prefix="/api", tags=["Quizzes"])


@router.post("/courses/{course_id}/quizzes", response_model=QuizOut, status_code=201)
def create_quiz(
    course_id: int,
    payload: QuizCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if user.role != "admin" and course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="Not the course owner")

    quiz = Quiz(
        course_id=course_id,
        title=payload.title,
        pass_mark=payload.pass_mark,
        max_attempts=payload.max_attempts,
    )
    db.add(quiz)
    db.flush()  # assign quiz.id before adding questions

    for q in payload.questions:
        db.add(
            Question(
                quiz_id=quiz.id,
                type=q.type,
                prompt=q.prompt,
                options=json.dumps(q.options),
                correct_answer=q.correct_answer,
                position=q.position,
            )
        )
    db.commit()
    db.refresh(quiz)
    return _quiz_out(quiz)


@router.get("/quizzes/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return _quiz_out(quiz)


@router.post("/quizzes/{quiz_id}/submit", response_model=AttemptResult)
def submit_quiz(
    quiz_id: int,
    payload: QuizSubmit,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.course_id == quiz.course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(status_code=403, detail="Enroll in the course before attempting")

    prior = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user.id
    ).count()
    if prior >= quiz.max_attempts:
        raise HTTPException(status_code=400, detail="Max attempts reached")

    questions = {q.id: q for q in quiz.questions}
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        enrollment_id=enrollment.id,
        user_id=user.id,
        attempt_number=prior + 1,
    )
    db.add(attempt)
    db.flush()

    correct = 0
    given = {a.question_id: a.answer for a in payload.answers}
    for qid, question in questions.items():
        ans = given.get(qid, "")
        is_correct = ans.strip().lower() == question.correct_answer.strip().lower()
        correct += int(is_correct)
        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                question_id=qid,
                answer_given=ans,
                is_correct=is_correct,
            )
        )

    total = len(questions)
    score = round(correct / total * 100, 2)
    attempt.score = score
    attempt.passed = score >= quiz.pass_mark
    db.commit()
    db.refresh(attempt)

    return AttemptResult(
        attempt_id=attempt.id,
        score=score,
        passed=attempt.passed,
        attempt_number=attempt.attempt_number,
        correct=correct,
        total=total,
    )


def _quiz_out(quiz: Quiz) -> QuizOut:
    """Serialize a quiz WITHOUT leaking correct answers."""
    return QuizOut(
        id=quiz.id,
        course_id=quiz.course_id,
        title=quiz.title,
        pass_mark=quiz.pass_mark,
        max_attempts=quiz.max_attempts,
        questions=[
            QuestionOut(
                id=q.id,
                type=q.type,
                prompt=q.prompt,
                options=json.loads(q.options or "[]"),
                position=q.position,
            )
            for q in sorted(quiz.questions, key=lambda x: x.position)
        ],
    )
