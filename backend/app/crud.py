from sqlalchemy.orm import Session
from . import models


def get_completed_courses(db: Session, student_id: int):
    """Returns a list of course_ids the student has completed."""
    completed = (
        db.query(models.CompletedCourse)
        .filter(models.CompletedCourse.student_id == student_id)
        .all()
    )
    return [c.course_id for c in completed]


def get_course_prerequisites(db: Session, course_id: int):
    """Returns a list of prerequisite_course_ids required for a given course."""
    prereqs = (
        db.query(models.CoursePrerequisite)
        .filter(models.CoursePrerequisite.course_id == course_id)
        .all()
    )
    return [p.prerequisite_course_id for p in prereqs]


def get_all_courses(db: Session):
    return db.query(models.Course).all()


def get_course_by_code(db: Session, course_code: str):
    return db.query(models.Course).filter(models.Course.course_code == course_code).first()