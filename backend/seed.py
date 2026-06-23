from datetime import time
from app.database import SessionLocal, engine, Base
from app import models

# Make sure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data (safe for repeated seeding during development)
db.query(models.CompletedCourse).delete()
db.query(models.CourseSection).delete()
db.query(models.CoursePrerequisite).delete()
db.query(models.Course).delete()
db.commit()

# --- Courses ---
courses_data = [
    {"course_code": "CSC 1301", "course_name": "Principles of Computer Science I", "credit_hours": 3, "department": "CSC", "description": "Intro to programming concepts."},
    {"course_code": "CSC 1302", "course_name": "Principles of Computer Science II", "credit_hours": 3, "department": "CSC", "description": "Continuation of CSC 1301."},
    {"course_code": "CSC 2510", "course_name": "Theoretical Foundations of Computer Science", "credit_hours": 3, "department": "CSC", "description": "Discrete math and logic for CS."},
    {"course_code": "CSC 2720", "course_name": "Data Structures", "credit_hours": 3, "department": "CSC", "description": "Core data structures and algorithms."},
    {"course_code": "CSC 3210", "course_name": "Computer Organization and Programming", "credit_hours": 3, "department": "CSC", "description": "Low-level systems and architecture."},
    {"course_code": "MATH 2211", "course_name": "Calculus of One Variable I", "credit_hours": 4, "department": "MATH", "description": "Differential calculus."},
    {"course_code": "MATH 2212", "course_name": "Calculus of One Variable II", "credit_hours": 4, "department": "MATH", "description": "Integral calculus."},
    {"course_code": "CSC 3320", "course_name": "Systems Programming", "credit_hours": 3, "department": "CSC", "description": "Programming closer to the OS level."},
    {"course_code": "CSC 4351", "course_name": "Database Systems", "credit_hours": 3, "department": "CSC", "description": "Relational database design and SQL."},
    {"course_code": "CSC 4520", "course_name": "Design and Analysis of Algorithms", "credit_hours": 3, "department": "CSC", "description": "Algorithm design paradigms and complexity."},
]

course_objects = {}
for c in courses_data:
    course = models.Course(**c)
    db.add(course)
    db.flush()  # so course.id is available
    course_objects[c["course_code"]] = course

db.commit()

# --- Prerequisites ---
prereq_pairs = [
    ("CSC 1302", "CSC 1301"),
    ("CSC 2720", "CSC 1302"),
    ("CSC 2510", "CSC 1301"),
    ("CSC 3210", "CSC 1302"),
    ("CSC 3320", "CSC 3210"),
    ("CSC 4351", "CSC 2720"),
    ("CSC 4520", "CSC 2720"),
    ("CSC 4520", "CSC 2510"),
    ("MATH 2212", "MATH 2211"),
]

for course_code, prereq_code in prereq_pairs:
    prereq = models.CoursePrerequisite(
        course_id=course_objects[course_code].id,
        prerequisite_course_id=course_objects[prereq_code].id,
    )
    db.add(prereq)

db.commit()

# --- Course Sections ---
sections_data = [
    ("CSC 1301", "001", "Dr. Smith", "MW", time(9, 0), time(10, 15)),
    ("CSC 1301", "002", "Dr. Lee", "TR", time(11, 0), time(12, 15)),
    ("CSC 1302", "001", "Dr. Smith", "MW", time(10, 30), time(11, 45)),
    ("CSC 2720", "001", "Dr. Patel", "MWF", time(9, 0), time(9, 50)),
    ("CSC 2720", "002", "Dr. Patel", "TR", time(13, 0), time(14, 15)),
    ("CSC 2510", "001", "Dr. Kim", "TR", time(9, 30), time(10, 45)),
    ("CSC 3210", "001", "Dr. Brown", "MW", time(12, 0), time(13, 15)),
    ("MATH 2211", "001", "Dr. Garcia", "MWF", time(8, 0), time(8, 50)),
    ("MATH 2211", "002", "Dr. Garcia", "TR", time(14, 0), time(15, 15)),
    ("MATH 2212", "001", "Dr. Garcia", "MWF", time(10, 0), time(10, 50)),  #new
    ("CSC 3320", "001", "Dr. Brown", "TR", time(10, 0), time(11, 15)),
    ("CSC 4351", "001", "Dr. Nguyen", "MW", time(14, 0), time(15, 15)),
    ("CSC 4520", "001", "Dr. Kim", "MWF", time(11, 0), time(11, 50)),
]

for course_code, section_number, professor, days, start, end in sections_data:
    section = models.CourseSection(
        course_id=course_objects[course_code].id,
        section_number=section_number,
        professor=professor,
        semester="Fall 2026",
        days_of_week=days,
        start_time=start,
        end_time=end,
        location="TBD",
        capacity=30,
    )
    db.add(section)

db.commit()

# --- Sample completed courses for student_id = 1 ---
completed = [
    ("CSC 1301", "Spring 2026", "A"),
    ("MATH 2211", "Spring 2026", "B"),
    ("CSC 1302", "Fall 2025", "B"),  #new
]

for course_code, semester, grade in completed:
    completed_course = models.CompletedCourse(
        student_id=1,
        course_id=course_objects[course_code].id,
        semester_completed=semester,
        grade=grade,
    )
    db.add(completed_course)

db.commit()
db.close()

print("Seed data inserted successfully.")