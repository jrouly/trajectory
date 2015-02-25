"""
trajectory/models/models.py
Author: Jean Michel Rouly

Define the models package.
"""


from sqlalchemy.orm import relationship, backref
from sqlalchemy import UniqueConstraint, ForeignKey, Column, Integer, String

from trajectory.models import meta


class University(meta.Base):
    """
    Full data about any particular university, including its web address,
    name, and any common abbreviation.
    """

    __tablename__ = "university"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    abbreviation = Column(String, nullable=False)
    url = Column(String)

    departments = relationship("Department", backref="university")

    def __repr__(self):
        return "<University: '%s'>" % self.name


class Department(meta.Base):
    """
    Full data about any department at a specific school.
    """

    __tablename__ = "department"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False)
    url = Column(String)
    university_id = Column(Integer, ForeignKey("university.id"))

    courses = relationship("Course", backref="department")

    def __repr__(self):
        if self.university is None:
            return "<Department: None '%s'>" % self.name
        return "<Department: '%s' '%s'>" % \
                (self.university.abbreviation,
                 self.name)


class Course(meta.Base):
    """
    A course offering, which belongs to a department at a school.
    """

    __tablename__ = "course"
    __table_args__ = (
            UniqueConstraint('number', 'title', 'department_id'),
            )

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    description_raw = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))
    parent_id = Column(Integer, ForeignKey("course.id"))

    prerequisites = relationship("Course")

    def __repr__(self):
        if self.department is None:
            return "<Course: None %s '%s'>" % \
                    (self.number, self.title)
        return "<Course: %s %s %s %s>" % \
                (self.department.university.name,
                 self.department.abbreviation,
                 self.number,
                 self.title)


# Register models with the database ORM mapping.
meta.Base.metadata.create_all(meta.Engine)
