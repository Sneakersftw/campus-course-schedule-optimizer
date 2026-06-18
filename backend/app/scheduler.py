from sqlalchemy.orm import Session
from . import crud, models


def check_prerequisites(db: Session, course_id: int, completed_course_ids: list[int]) -> bool:
    """
    Returns True if the student has completed all prerequisites for course_id.
    Courses with no prerequisites always return True.
    """
    required = crud.get_course_prerequisites(db, course_id)
    if not required:
        return True
    return all(prereq_id in completed_course_ids for prereq_id in required)


def get_eligible_courses(db: Session, student_id: int):
    """
    Returns a list of Course objects the student is eligible to take,
    based on completed prerequisites. Already-completed courses are excluded.
    """
    completed_course_ids = crud.get_completed_courses(db, student_id)
    all_courses = crud.get_all_courses(db)

    eligible = []
    for course in all_courses:
        if course.id in completed_course_ids:
            continue  # already taken, skip
        if check_prerequisites(db, course.id, completed_course_ids):
            eligible.append(course)

    return eligible
