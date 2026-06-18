import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import time
from app import scheduler


class FakeCourse:
    def __init__(self, credit_hours, sections):
        self.credit_hours = credit_hours
        self.sections = sections


class FakeSection:
    def __init__(self, course, days, start, end):
        self.course = course
        self.days_of_week = days
        self.start_time = start
        self.end_time = end


def test_generates_schedule_within_credit_range():
    course_a = FakeCourse(credit_hours=3, sections=[])
    course_b = FakeCourse(credit_hours=3, sections=[])

    section_a = FakeSection(course_a, "MW", time(9, 0), time(10, 0))
    section_b = FakeSection(course_b, "TR", time(9, 0), time(10, 0))
    course_a.sections = [section_a]
    course_b.sections = [section_b]

    schedules = scheduler.generate_valid_schedules(
        [course_a, course_b], min_credits=4, max_credits=8
    )

    assert len(schedules) >= 1
    assert all(4 <= scheduler.calculate_credit_hours(s) <= 8 for s in schedules)


def test_excludes_schedules_outside_credit_range():
    course_a = FakeCourse(credit_hours=3, sections=[])
    section_a = FakeSection(course_a, "MW", time(9, 0), time(10, 0))
    course_a.sections = [section_a]

    # Only one 3-credit course, but we require at least 10 credits
    schedules = scheduler.generate_valid_schedules(
        [course_a], min_credits=10, max_credits=18
    )

    assert len(schedules) == 0


def test_conflicting_sections_never_appear_together():
    course_a = FakeCourse(credit_hours=3, sections=[])
    course_b = FakeCourse(credit_hours=3, sections=[])

    # Both sections overlap on Monday/Wednesday at the same time
    section_a = FakeSection(course_a, "MW", time(9, 0), time(10, 0))
    section_b = FakeSection(course_b, "MW", time(9, 30), time(10, 30))
    course_a.sections = [section_a]
    course_b.sections = [section_b]

    schedules = scheduler.generate_valid_schedules(
        [course_a, course_b], min_credits=0, max_credits=20
    )

    for schedule in schedules:
        assert not (section_a in schedule and section_b in schedule)


def test_course_with_multiple_sections_offers_choice():
    course_a = FakeCourse(credit_hours=3, sections=[])
    section_1 = FakeSection(course_a, "MW", time(9, 0), time(10, 0))
    section_2 = FakeSection(course_a, "TR", time(13, 0), time(14, 0))
    course_a.sections = [section_1, section_2]

    schedules = scheduler.generate_valid_schedules(
        [course_a], min_credits=3, max_credits=3
    )

    # Should generate two valid schedules: one with each section
    assert len(schedules) == 2