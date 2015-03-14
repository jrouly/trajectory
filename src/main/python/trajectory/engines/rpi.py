"""
trajectory/engines/rpi_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to RPI's CS department.
"""


from trajectory.models import University, Department, Course
from trajectory.models.meta import session
from trajectory.core import clean
from trajectory import config as TRJ
from bs4 import BeautifulSoup
import requests, re, os, json


def scrape(args):
    """
    Scrape the available syllabi from the RPI CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping RPI CS data." )


    # Generate a BeautifulSoup object.
    catalog_index_url = "http://catalog.rpi.edu/content.php?filter[27]=CSCI&cur_cat_oid=13&navoid=313"
    catalog_index = requests.get( catalog_index_url )
    soup = BeautifulSoup( catalog_index.text )

    # Identify the list of courses.
    course_list = soup.find_all(
            name="a",
            onclick=re.compile("showCourse.*"))

    # Select only the catoid and coid.
    catoid_re = re.compile("(?<=catoid=)\d+")
    coid_re = re.compile("(?<=coid=)\d+")

    # Piecewise course page url.
    course_url = "http://catalog.rpi.edu/preview_course_nopop.php?catoid=%s&coid=%s"

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
        course_page = requests.get( course_url % (catoid, coid) )
        course_soup = BeautifulSoup( course_page.text )
        content = course_soup.find(class_="block_content").hr.text

        # Clean up the description.
        description = content
        try:
            description = description[:description.index("Credit Hours")]
            description = description[:description.index("When Offered")]
        except:
            pass

        # Identify prerequisites
        # TODO: Match these up with their database entries.
        prereq_index = description.find("Prerequisit")
        if prereq_index > -1:
            prereq_string = description[prereq_index:]
            description = description[:prereq_index]

            prereq_re = re.compile("\w{2,4}\s\d{3}")
            matches = re.findall(prereq_re, prereq_string)
            if len(matches) > 0:
                prereqs["%s %s" % (prefix, cnum)] = matches

        # Clean the description string
        description_raw = description
        description = clean(description)
        if description is None:
            continue

        # Generate the appropriate course object.
        departments[prefix.lower()].courses.append(Course(
            number=cnum,
            title=title,
            description_raw=description,
            description=description))

    log.info( "Completed scraping." )


# Constant values.
_json = open(os.path.join(TRJ.ENGINE_METADATA, "rpi.json"))
META = json.load(_json)
_json.close()


