from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import scheduler

router = APIRouter()


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

    results = []
    for schedule in ranked[:5]:  # top 5 only
        results.append({
            "score": scheduler.score_schedule(schedule),
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
        })

    return {"student_id": student_id, "schedule_count": len(ranked), "top_schedules": results}