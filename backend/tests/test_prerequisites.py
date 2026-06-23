import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import crud, scheduler


def get_test_db():
    return SessionLocal()


def test_course_with_no_prerequisites_is_eligible():
    db = get_test_db()
    csc_1301 = crud.get_course_by_code(db, "CSC 1301")
    result = scheduler.check_prerequisites(db, csc_1301.id, completed_course_ids=[])
    db.close()
    assert result is True


def test_student_missing_prerequisite():
    db = get_test_db()
    csc_2720 = crud.get_course_by_code(db, "CSC 2720")  # requires CSC 1302
    result = scheduler.check_prerequisites(db, csc_2720.id, completed_course_ids=[])
    db.close()
    assert result is False


def test_student_completed_prerequisite():
    db = get_test_db()
    csc_1302 = crud.get_course_by_code(db, "CSC 1302")
    csc_2720 = crud.get_course_by_code(db, "CSC 2720")
    result = scheduler.check_prerequisites(
        db, csc_2720.id, completed_course_ids=[csc_1302.id]
    )
    db.close()
    assert result is True


def test_course_requiring_two_prerequisites():
    db = get_test_db()
    csc_2720 = crud.get_course_by_code(db, "CSC 2720")
    csc_2510 = crud.get_course_by_code(db, "CSC 2510")
    csc_4520 = crud.get_course_by_code(db, "CSC 4520")  # requires both
    result = scheduler.check_prerequisites(
        db, csc_4520.id, completed_course_ids=[csc_2720.id, csc_2510.id]
    )
    db.close()
    assert result is True


def test_student_with_unrelated_completed_course():
    db = get_test_db()
    math_2211 = crud.get_course_by_code(db, "MATH 2211")
    csc_2720 = crud.get_course_by_code(db, "CSC 2720")  # requires CSC 1302, unrelated to MATH 2211
    result = scheduler.check_prerequisites(
        db, csc_2720.id, completed_course_ids=[math_2211.id]
    )
    db.close()
    assert result is False


def test_get_eligible_courses_for_sample_student():
    db = get_test_db()
    eligible = scheduler.get_eligible_courses(db, student_id=1)
    eligible_codes = [c.course_code for c in eligible]
    db.close()
    # Student 1 has completed CSC 1301, MATH 2211, and CSC 1302
    assert "CSC 2720" in eligible_codes  # needs CSC 1302, which is now done
    assert "CSC 1301" not in eligible_codes  # already completed, should be excluded
    assert "CSC 1302" not in eligible_codes  # already completed, should be excluded
    