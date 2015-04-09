"""
trajectory/engines/sc_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to SC's CS department.
"""


from trajectory.models import University, Course, Department
from trajectory.models.meta import session
from trajectory.core import clean
from trajectory import config as TRJ
from bs4 import BeautifulSoup
import requests, re, os, json


def scrape(args):
    """
    Scrape the available syllabi from the SC CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info("Scraping SC CS data.")


    # Generate a BeautifulSoup object.
    catalog_index_url = "http://bulletin.sc.edu/content.php?catoid=36&navoid=4242&filter[27]=CSCE"
    catalog_index = requests.get(catalog_index_url)
    soup = BeautifulSoup(catalog_index.text)

    # Identify the list of courses.
    course_list = soup.find_all(
            name="a",
            onclick=re.compile("showCourse.*"))

    # Select only the catoid and coid.
    catoid_re = re.compile("(?<=catoid=)\d+")
    coid_re = re.compile("(?<=coid=)\d+")

    # Piecewise course page url.
    course_url = "http://bulletin.sc.edu/preview_course.php?catoid=%s&coid=%s"

    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = session.query(University)\
            .filter(University.name==university)\
            .first()
    departments = {department.abbreviation.lower() : department
                    for department in session.query(Department)\
                        .filter(Department.university==university)\
                        .all()}

    # Identify relevant information for each course.
    prereqs = {}
    for course in course_list:

        # Generate metadata
        log.debug(course.text)
        full_title = re.compile("\s+").split(course.text)
        prefix = full_title[0]
        cnum = full_title[1]
        title = ' '.join(full_title[3:])
        title = title.replace("'", "")

        # Identify coid to get description.
        href = course['href']
        catoid = catoid_re.search(href).group(0)
        coid = coid_re.search(href).group(0)

        # Generate a BeautifulSoup object of the course description.
        course_page = requests.get(course_url % (catoid, coid))
        course_soup = BeautifulSoup(course_page.text)
        content = course_soup.h1.next_sibling.next_sibling.text

        # Clean up the description.
        def strip_substring(body, substring):
            try:    return body[:body.index(substring)]
            except: return body

        # Clean the content string
        content = strip_substring(content, "Print-Friendly Page Close Window")

        # Clean the description string
        description_raw = content
        description_raw = strip_substring(description_raw, "Prereq")
        description_raw = strip_substring(description_raw, "Coreq")
        description_raw = strip_substring(description_raw, "Note:")
        description_raw = strip_substring(description_raw, "Cross-listed")

        description = clean(description_raw)
        if description is None:
            continue

        # Generate the appropriate course object.
        departments[prefix.lower()].courses.append(Course(
            number=cnum,
            title=title,
            description_raw=description_raw,
            description=description))

    log.info( "Completed scraping." )


# Constant values.
_json = open(os.path.join(TRJ.ENGINE_METADATA, "sc.json"))
META = json.load(_json)
_json.close()


