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
def score_schedule(schedule: list, preferences: dict = None) -> int:
    """
    Scores a valid schedule. Higher is better.
    preferences is an optional dict that can include:
      - earliest_class_time (datetime.time)
      - avoid_days (list of single-character day codes, e.g. ["F"])
      - prefer_fewer_days (bool)
    """
    if preferences is None:
        preferences = {}

    score = 100

    # Penalize gaps between classes on the same day
    score -= _total_gap_minutes(schedule) // 30

    # Penalize classes that start before the preferred earliest time
    earliest = preferences.get("earliest_class_time")
    if earliest:
        for section in schedule:
            if section.start_time < earliest:
                score -= 10

    # Penalize classes on days the student wants to avoid
    avoid_days = preferences.get("avoid_days", [])
    for section in schedule:
        for day in avoid_days:
            if day in section.days_of_week:
                score -= 15

    # Reward fewer distinct class days, if preferred
    if preferences.get("prefer_fewer_days"):
        distinct_days = set()
        for section in schedule:
            distinct_days.update(section.days_of_week)
        score += (5 - len(distinct_days)) * 2  # more bonus for fewer days

    return score


def _total_gap_minutes(schedule: list) -> int:
    """Sums gap time between classes on the same day, across the whole schedule."""
    from collections import defaultdict

    by_day = defaultdict(list)
    for section in schedule:
        for day in section.days_of_week:
            by_day[day].append(section)

    total_gap = 0
    for day, sections in by_day.items():
        sections_sorted = sorted(sections, key=lambda s: s.start_time)
        for i in range(len(sections_sorted) - 1):
            end = sections_sorted[i].end_time
            start = sections_sorted[i + 1].start_time
            gap_minutes = (start.hour * 60 + start.minute) - (end.hour * 60 + end.minute)
            if gap_minutes > 0:
                total_gap += gap_minutes

    return total_gap


def rank_schedules(schedules: list, preferences: dict = None) -> list:
    """Returns schedules sorted from highest score to lowest."""
    scored = [(score_schedule(s, preferences), s) for s in schedules]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [s for score, s in scored]

def schedule_violates_avoided_days(schedule: list, avoid_days: list) -> bool:
    """
    Returns True if any section in the schedule falls on a day the student
    explicitly wants to avoid.
    """
    if not avoid_days:
        return False
    for section in schedule:
        for day in avoid_days:
            if day in section.days_of_week:
                return True
    return False