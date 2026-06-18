import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import time
from app.database import SessionLocal
from app import crud, scheduler


def get_test_db():
    return SessionLocal()


class FakeSection:
    """A lightweight stand-in for CourseSection, used for isolated logic tests."""
    def __init__(self, days, start, end, credit_hours=3):
        self.days_of_week = days
        self.start_time = start
        self.end_time = end

        class FakeCourse:
            pass
        self.course = FakeCourse()
        self.course.credit_hours = credit_hours


def test_same_day_overlapping_sections_conflict():
    a = FakeSection("MW", time(9, 0), time(10, 15))
    b = FakeSection("MW", time(9, 30), time(10, 45))
    assert scheduler.sections_overlap(a, b) is True


def test_different_days_do_not_conflict():
    a = FakeSection("MW", time(9, 0), time(10, 15))
    b = FakeSection("TR", time(9, 0), time(10, 15))
    assert scheduler.sections_overlap(a, b) is False


def test_back_to_back_classes_do_not_conflict():
    a = FakeSection("MW", time(9, 0), time(10, 0))
    b = FakeSection("MW", time(10, 0), time(11, 0))
    assert scheduler.sections_overlap(a, b) is False


def test_partial_overlap_conflicts():
    a = FakeSection("TR", time(9, 0), time(10, 30))
    b = FakeSection("TR", time(10, 0), time(11, 0))
    assert scheduler.sections_overlap(a, b) is True


def test_calculate_credit_hours_sums_correctly():
    a = FakeSection("MW", time(9, 0), time(10, 0), credit_hours=3)
    b = FakeSection("TR", time(11, 0), time(12, 0), credit_hours=4)
    total = scheduler.calculate_credit_hours([a, b])
    assert total == 7


def test_schedule_with_no_conflicts():
    a = FakeSection("MW", time(9, 0), time(10, 0))
    b = FakeSection("TR", time(9, 0), time(10, 0))
    assert scheduler.schedule_has_conflicts([a, b]) is False


def test_schedule_with_one_conflict():
    a = FakeSection("MW", time(9, 0), time(10, 0))
    b = FakeSection("MW", time(9, 30), time(10, 30))
    c = FakeSection("TR", time(13, 0), time(14, 0))
    assert scheduler.schedule_has_conflicts([a, b, c]) is True
    