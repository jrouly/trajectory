"""
trajectory/engines/utk.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to Univserity of Tennessee's course
catalog.
"""


from trajectory.models import University, Department, Course
from trajectory.models.meta import session
from trajectory.core import clean
from trajectory import config as TRJ
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from sqlalchemy import func
import requests, re, os, json


def scrape(args):
    """
    Scrape the available syllabi from the UTK catalog into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info("Scraping UTK data.")


    # Constant values.
    catalog_index_url = "http://catalog.utk.edu/preview_course_incoming.php?prefix=%s&catoid=18"
    course_url = "http://catalog.utk.edu/preview_course.php?catoid=%s&coid=%s"

    # Regex to select only the catid and coid.
    catid_re = re.compile("(^[^']*)|(, this.*$)|(')")

    # Regex to isolate prerequisite course titles.
    prereq_re = re.compile("(\s|\\\\xa0)(\d{3})")

    # List of prefixes from the META object.
    prefixes = [department.get("abbreviation").lower()
                    for department in META.get("departments")]

    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = session.query(University)\
            .filter(University.name==university)\
            .first()
    departments = {department.abbreviation.lower() : department
                    for department in session.query(Department)\
                        .filter(Department.university==university)\
                        .all()}

    prereq_dict = {} # Dictionary of Course : Prereq match list
    for prefix in prefixes:
        if args.cs and prefix not in ["cosc"]: continue
        catalog_index = requests.get(catalog_index_url % prefix)
        soup = BeautifulSoup(catalog_index.text)

        # Identify the list of courses.
        course_list = soup.find_all(
                name="a",
                onclick=re.compile("showCourse.*"))

        # Identify relevant information for each course.
        for course in course_list:

            # Generate metadata
            log.debug(course.text)
            full_title = re.compile("\s+").split(course.text)
            cnum = full_title[1]
            title = ' '.join(full_title[3:])

            # Identify coid to get description.
            onclick = course['onclick']
            (catid, coid) = re.sub(catid_re, "", onclick).split(", ")

            # Generate a BeautifulSoup object of the course description.
            course_page = requests.get(course_url % (catid, coid))
            course_soup = BeautifulSoup(course_page.text)
            content = course_soup.find(class_="block_content_popup").hr

            # Clean out garbage
            [div.extract() for div in content.find_all("div")]
            extra = ' '.join([em.extract().text
                    for em in content.find_all("em")])
            extra.strip(' ')

            # Clean up the description
            description_raw = content.text.replace('\n', '').strip(' ')
            description = clean(description_raw)
            if description is None:
                continue

            # Identify prerequisites
            prereq_index = extra.find("requisite")
            prereq_list = None
            if prereq_index > -1:

                prereq_string = extra[prereq_index:]
                matches = prereq_re.findall(prereq_string)

                if len(matches) > 0:
                    # Split them up as a dict and store them in a list.
                    # Naiive assumption that every course number is within
                    # the same department because the department titles are
                    # written out and not matchable.
                    prereq_list = [{
                            "d": prefix.lower(), # department
                            "n": match[-1]  # number
                        } for match in matches]

            # Generate the appropriate course object.
            new_course = Course(
                number=cnum,
                title=title,
                description=description,
                description_raw=description_raw)
            departments[prefix.lower()].courses.append(new_course)

            # Add in the requested list of prereqs if found.
            if prereq_list is not None:
                prereq_dict[new_course] = prereq_list

    # Iterate over the list of courses, now that they've been created, and
    # process their list of requested prerequisites.
    for course, prereq_list in prereq_dict.items():

        # Skip any courses with a 0-length requested prereq list.
        if len(prereq_list) == 0:
            continue

        log.debug(course)
        log.debug(prereq_list)

        # Loop over set of prereqs, if there are multiple.
        department_stack = []
        for prereq in prereq_list:
            n = prereq.get("n") # prereq course number
            d = prereq.get("d") # prereq course department abbreviation

            log.debug("Searching for: %s %s" % (d, n))

            # Reference the prerequisite course identified by this
            # department abbreviation and course number.
            prereq_course = session.query(Course) \
                    .join(Department) \
                    .filter(Department.university==university) \
                    .filter(func.lower(Department.abbreviation)==d.lower()) \
                    .filter(Course.number==int(n)) \
                    .first()

            # If a valid course was found, tack it onto the prereq list of
            # the requesting course (course).
            if prereq_course and prereq_course is not course:
                course.prerequisites.append(prereq_course)
            else:
                log.debug("Failed to find course matching '%s %s'." % (d, n))

    log.info("Completed scraping.")


# Constant values.
_json = open(os.path.join(TRJ.ENGINE_METADATA, "utk.json"))
META = json.load(_json)
_json.close()


