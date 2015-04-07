"""
trajectory/engines/acm.py
Author: Jean Michel Rouly

This file will read the ACM text into the database.
"""


from trajectory.models import University, Department, Course
from trajectory.models.meta import session
from trajectory.core import clean
from trajectory import config as TRJ
from sqlalchemy import func
import re, os, json


def scrape(args):
    """
    Manipulate the ACM textual data and store it in the database.
    """


    import logging
    log = logging.getLogger("root")
    log.info("Scraping ACM data.")


    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = session.query(University)\
            .filter(University.name==university)\
            .first()

    def load_acm_file(department, data_file):
        while True:
            title = data_file.readline().rstrip('\n')
            description_raw = data_file.readline().rstrip('\n')
            if not description_raw: break

            # Clean the description
            description = clean(description_raw)
            if description is None:
                continue

            # Generate the appropriate course object.
            new_course = Course(
                number=0, # blank out course numbers
                title=title,
                description=description,
                description_raw=description_raw)
            department.courses.append(new_course)


    exemplar_courses = session.query(Department)\
            .filter(Department.university==university)\
            .filter(Department.abbreviation=="EC")\
            .first()
    data_file = open(TRJ.ACM_EXEMPLARS)
    load_acm_file(exemplar_courses, data_file)
    data_file.close()

    knowledge_areas = session.query(Department)\
            .filter(Department.university==university)\
            .filter(Department.abbreviation=="KA")\
            .first()
    data_file = open(TRJ.ACM_KA)
    load_acm_file(knowledge_areas, data_file)
    data_file.close()


    log.info("Completed scraping.")


# Constant values.
_json = open(os.path.join(TRJ.ENGINE_METADATA, "acm.json"))
META = json.load(_json)
_json.close()


