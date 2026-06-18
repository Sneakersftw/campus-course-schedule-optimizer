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

def sections_overlap(section_a, section_b) -> bool:
    """
    Returns True if two course sections conflict — meaning they share
    at least one day AND their time ranges overlap.
    """
    days_a = set(section_a.days_of_week)
    days_b = set(section_b.days_of_week)

    if not days_a.intersection(days_b):
        return False  # no shared days, cannot conflict

    # Times overlap if one starts before the other ends, in both directions
    return section_a.start_time < section_b.end_time and section_b.start_time < section_a.end_time

def calculate_credit_hours(schedule: list) -> int:
    """Sums credit hours for a list of CourseSection objects (via their parent Course)."""
    return sum(section.course.credit_hours for section in schedule)

def schedule_has_conflicts(schedule: list) -> bool:
    """
    Returns True if ANY two sections in the schedule conflict.
    """
    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            if sections_overlap(schedule[i], schedule[j]):
                return True
    return False

def generate_valid_schedules(eligible_courses, min_credits=12, max_credits=18):
    """
    Generates all valid schedules from eligible courses.
    Each course contributes at most one section (or is skipped entirely).
    A valid schedule has no time conflicts and falls within the credit range.
    """
    all_schedules = []

    def backtrack(course_index, current_schedule):
        # Base case: considered every course
        if course_index == len(eligible_courses):
            credits = calculate_credit_hours(current_schedule)
            if min_credits <= credits <= max_credits and not schedule_has_conflicts(current_schedule):
                all_schedules.append(list(current_schedule))
            return

        course = eligible_courses[course_index]

        # Option 1: skip this course entirely
        backtrack(course_index + 1, current_schedule)

        # Option 2: try each section of this course
        for section in course.sections:
            current_schedule.append(section)
            # Prune early: stop exploring this branch if it already conflicts
            if not schedule_has_conflicts(current_schedule):
                backtrack(course_index + 1, current_schedule)
            current_schedule.pop()

    backtrack(0, [])
    return all_schedules