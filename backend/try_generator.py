
from app.database import SessionLocal
from app import scheduler

db = SessionLocal()

eligible = scheduler.get_eligible_courses(db, student_id=1)
print(f"Eligible courses for student 1: {[c.course_code for c in eligible]}")

schedules = scheduler.generate_valid_schedules(eligible, min_credits=6, max_credits=16)
print(f"\nGenerated {len(schedules)} valid schedules within 12-16 credits.\n")

for i, schedule in enumerate(schedules[:5], start=1):
    total = scheduler.calculate_credit_hours(schedule)
    courses_in_schedule = [s.course.course_code for s in schedule]
    print(f"Schedule {i} ({total} credits): {courses_in_schedule}")

db.close()