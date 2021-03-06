"""
trajectory/models/models.py
Author: Jean Michel Rouly

Define the models package.
"""


from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, UniqueConstraint, ForeignKey, ForeignKeyConstraint
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import desc

from datetime import datetime

from trajectory.models import meta


class ResultSet(meta.Base):
    """
    Meta model to track different result sets and allow for multiple
    results in a single database.
    """

    __tablename__ = "result_set"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)

    alpha = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)
    iterations = Column(Float, nullable=True)
    num_topics = Column(Integer, nullable=True)

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __repr__(self):
        return "<ResultSet: %d>" % self.id

class University(meta.Base):
    """
    Full data about any particular university, including its web address,
    name, and any common abbreviation.
    """

    __tablename__ = "university"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    abbreviation = Column(String, unique=True, nullable=False)
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


# Maintain a mapping of courses to courses to define the prerequisite
# relationship structure.
course_to_course = Table("course_to_course", meta.Base.metadata,
    Column("parent_id",
        Integer,
        ForeignKey("course.id"),
        primary_key=True),
    Column("prerequisite_id",
        Integer,
        ForeignKey("course.id"),
        primary_key=True)
)


class Course(meta.Base):
    """
    A course offering, which belongs to a department at a school.
    """

    __tablename__ = "course"

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    description_raw = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))

    prerequisites = relationship("Course",
                        secondary=course_to_course,
                        primaryjoin=id==course_to_course.c.parent_id,
                        secondaryjoin=id==course_to_course.c.prerequisite_id,
                        backref="parents")

    topics = relationship(
            "CourseTopicAssociation",
            backref="course",
            order_by=desc("course_topic_association.proportion"))

    def __repr__(self):
        if self.department is None:
            return "<Course: None %s '%s'>" % \
                    (self.number, self.title)
        return "<Course: %s %s %s %s>" % \
                (self.department.university.name,
                 self.department.abbreviation,
                 self.number,
                 self.title)


class Topic(meta.Base):
    """
    A statistically generated 'topic' which represents the concepts covered
    in a document.
    """

    __tablename__ = "topic"
    id = Column(Integer, primary_key=True)
    result_set_id = Column(Integer,
            ForeignKey("result_set.id"),
            primary_key=True,
            nullable=False)
    result_set = relationship("ResultSet", uselist=False)

    words = Column(String, nullable=False)

    def __repr__(self):
        return "<Topic: %s (%d)>" % (self.id, self.result_set_id)


class CourseTopicAssociation(meta.Base):
    """
    Define an association between a topic and a course.
    """

    __tablename__ = "course_topic_association"
    course_id = Column(Integer, ForeignKey("course.id"), primary_key=True)
    topic_id = Column(Integer, primary_key=True)
    result_set_id = Column(Integer, primary_key=True)
    proportion = Column(Float)

    topic = relationship("Topic",
            backref=backref("course_assocs",
                cascade="all, delete-orphan",
                order_by=desc("course_topic_association.proportion")))

    __table_args__ = (
            ForeignKeyConstraint(
                ['topic_id', 'result_set_id'],
                ['topic.id', 'topic.result_set_id']
            ),
    )

    def __repr__(self):
        return "<TopicAssociation (RS %d): (Topic %s, Course %s, Weight %s)>" % \
                (self.result_set_id, self.topic_id, self.course_id, self.proportion)

    def __lt__(self, other):
        return self.proportion < other.proportion

# Register models with the database ORM mapping.
meta.Base.metadata.create_all(meta.Engine)
