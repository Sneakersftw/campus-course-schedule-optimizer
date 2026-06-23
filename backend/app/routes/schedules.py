from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app import scheduler

router = APIRouter()


class UnavailableTime(BaseModel):
    days: list[str]
    start_time: str
    end_time: str


class PreferencesRequest(BaseModel):
    target_credit_hours: Optional[int] = None
    unavailable_times: list[UnavailableTime] = []
    earliest_class_time: Optional[str] = None
    latest_class_time: Optional[str] = None
    avoid_days: list[str] = []


def _day_to_letter(day_name: str) -> str:
    """Converts a full day name to the single-letter code used in days_of_week."""
    mapping = {
        "Monday": "M", "Tuesday": "T", "Wednesday": "W",
        "Thursday": "R", "Friday": "F", "Saturday": "S", "Sunday": "U",
    }
    return mapping.get(day_name, "")


def _format_schedule(schedule, score):
    return {
        "score": score,
        "total_credits": scheduler.calculate_credit_hours(schedule),
        "courses": [
            {
                "course_code": section.course.course_code,
                "course_name": section.course.course_name,
                "section_number": section.section_number,
                "professor": section.professor,
                "days_of_week": section.days_of_week,
                "start_time": section.start_time.strftime("%H:%M"),
                "end_time": section.end_time.strftime("%H:%M"),
            }
            for section in schedule
        ],
    }


@router.get("/schedules/{student_id}")
def get_schedules(
    student_id: int,
    min_credits: int = 12,
    max_credits: int = 18,
    db: Session = Depends(get_db),
):
    eligible = scheduler.get_eligible_courses(db, student_id)
    schedules = scheduler.generate_valid_schedules(eligible, min_credits, max_credits)
    ranked = scheduler.rank_schedules(schedules)

    results = [
        _format_schedule(schedule, scheduler.score_schedule(schedule))
        for schedule in ranked[:5]
    ]

    return {"student_id": student_id, "schedule_count": len(ranked), "top_schedules": results}


@router.post("/schedules/{student_id}/with-preferences")
def get_schedules_with_preferences(
    student_id: int,
    preferences: PreferencesRequest,
    db: Session = Depends(get_db),
):
    min_credits = preferences.target_credit_hours - 3 if preferences.target_credit_hours else 6
    max_credits = preferences.target_credit_hours + 3 if preferences.target_credit_hours else 18

    eligible = scheduler.get_eligible_courses(db, student_id)
    schedules = scheduler.generate_valid_schedules(eligible, min_credits, max_credits)

    scoring_prefs = {
        "avoid_days": [_day_to_letter(d) for d in preferences.avoid_days],
        "prefer_fewer_days": False,
    }
    if preferences.earliest_class_time:
        try:
            scoring_prefs["earliest_class_time"] = datetime.strptime(
                preferences.earliest_class_time, "%H:%M"
            ).time()
        except ValueError:
            pass  # ignore malformed time strings rather than crashing the request

    ranked = scheduler.rank_schedules(schedules, scoring_prefs)

    results = [
        _format_schedule(schedule, scheduler.score_schedule(schedule, scoring_prefs))
        for schedule in ranked[:5]
    ]

    return {
        "student_id": student_id,
        "applied_preferences": preferences.dict(),
        "schedule_count": len(ranked),
        "top_schedules": results,
    }