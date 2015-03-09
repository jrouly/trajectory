"""
trajectory/models/__init__.py
Author: Jean Michel Rouly

Collect the models and database meta objects into one module.
"""


from trajectory.models import meta
from trajectory.models.models import University, Department, Course
from trajectory.models.models import Topic, CourseTopicAssociation, ResultSet

__all__ = [
    "University",
    "Department",
    "Course",
    "Topic",
    "CourseTopicAssociation",
    "ResultSet",
    "meta"
]
