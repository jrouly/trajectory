"""
trajectory/engines/ksu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to Kansas State's CS department.
"""


from trajectory.models import University, Department, Course
from trajectory.models.meta import session
from trajectory.core import clean
from trajectory import config as TRJ
from bs4 import BeautifulSoup
from sqlalchemy import func
import requests, re, os, json


def scrape(args):
    """
    Scrape the available syllabi from the KSU CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping KSU data." )


    # Constant values.
    catalog_index_url = "http://catalog.k-state.edu/content.php?filter[27]=%s&cur_cat_oid=13&navoid=1425"
    course_url = "http://catalog.k-state.edu/preview_course_nopop.php?catoid=%s&coid=%s"

    # Scraper regexes.
    catoid_re = re.compile("(?<=catoid=)\d+")
    coid_re = re.compile("(?<=coid=)\d+")
    prereq_re = re.compile("([A-Za-z,]{2,5})(\s|\\\\xa0)(\d{3})")

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

            # Identify the components of the description and its metadata.
            result_set = course_soup.find(class_="block_content") \
                    .table \
                    .find_next_sibling("p") \
                    .h1 \
                    .find_next_siblings()

            # Join them together as text.
            content = ' '.join([r.text for r in result_set[1:]])

            # Clean up the description.
            description = content
            try:
                description = description[:description.index("When Offered")]
            except:
                pass
            try:
                description = description[:description.index("UGE course")]
            except:
                pass

            # Identify prerequisites.
            prereq_index = description.find("Requisites")
            prereq_list = None
            if prereq_index > -1:

                # Grab the substring of prereqs and find matches.
                prereq_string = description[prereq_index:]
                description = description[:prereq_index]
                matches = prereq_re.findall(prereq_string)

                if len(matches) > 0:
                    # Split them up as a dict and store them in a list.
                    prereq_list = [{
                            "d": match[0], # department
                            "n": match[2]  # number
                        } for match in matches]

            # Clean up the description some more.
            try:
                description = description[:description.index(".Note")]
            except:
                pass

            # Clean the description string
            description_raw = content
            description = clean(description_raw)
            if description is None:
                continue

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

            # If this is a referential prereq, look up the last course
            # observed and hope it's the correct department prefix.
            try:
                if d in ["and", "or", ","]:
                    d = department_stack[-1]
                department_stack.append(d)
            except IndexError: # no previous courses
                continue

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
_json = open(os.path.join(TRJ.ENGINE_METADATA, "ksu.json"))
META = json.load(_json)
_json.close()


