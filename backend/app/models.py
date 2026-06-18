from sqlalchemy import Column, Integer, String, ForeignKey, Time, Text
from sqlalchemy.orm import relationship
from .database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), unique=True, nullable=False)
    course_name = Column(String(200), nullable=False)
    credit_hours = Column(Integer, nullable=False)
    department = Column(String(100))
    description = Column(Text)

    sections = relationship("CourseSection", back_populates="course")
    prerequisites = relationship(
        "CoursePrerequisite",
        foreign_keys="CoursePrerequisite.course_id",
        back_populates="course",
    )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    prerequisite_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    course = relationship(
        "Course", foreign_keys=[course_id], back_populates="prerequisites"
    )
    prerequisite_course = relationship("Course", foreign_keys=[prerequisite_course_id])


class CourseSection(Base):
    __tablename__ = "course_sections"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    section_number = Column(String(10), nullable=False)
    professor = Column(String(100))
    semester = Column(String(20))
    days_of_week = Column(String(20))  # e.g. "MW", "TR", "MWF"
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String(100))
    capacity = Column(Integer)

    course = relationship("Course", back_populates="sections")


class CompletedCourse(Base):
    __tablename__ = "completed_courses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester_completed = Column(String(20))
    grade = Column(String(5))

    course = relationship("Course")