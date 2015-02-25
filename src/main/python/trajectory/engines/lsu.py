"""
trajectory/engines/lsu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to LSU's CS department.
"""


from trajectory.models import University, Course, Department
from trajectory.core import clean
from bs4 import BeautifulSoup
import requests
import re
import os


# Constant values.
META = {
    'school': {
        'name': "Louisiana State University",
        'abbreviation': "LSU",
        'url': "lsu.edu",
    },
    'departments': [
        {
            'name': "Computer Science",
            'abbreviation': "CSC",
            'url': "cse.lsu.edu",
        },
    ]
}


def scrape(args):
    """
    Scrape the available syllabi from the LSU CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping LSU CS data." )


    # Generate a BeautifulSoup object.
    catalog_index_url = "http://catalog.lsu.edu/content.php?filter[27]=CSC&cur_cat_oid=6&navoid=538"
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
    course_url = "http://catalog.lsu.edu/preview_course_nopop.php?catoid=%s&coid=%s"

    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = args.session.query(University)\
            .filter(University.name==university)\
            .first()
    departments = {department.abbreviation.lower() : department
                    for department in args.session.query(Department)\
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
        title = ' '.join(full_title[2:-1])
        title = title.replace("'", "")

        # Identify coid to get description.
        href = course['href']
        catoid = catoid_re.search(href).group(0)
        coid = coid_re.search(href).group(0)

        # Generate a BeautifulSoup object of the course description.
        course_page = requests.get(course_url % (catoid, coid))
        course_soup = BeautifulSoup(course_page.text)
        content = course_soup.find(class_="block_content").hr

        # Remove the metadata.
        [em.decompose() for em in content.find_all("em") if True]

        # Clean the description string
        description = clean(args, content.text)
        if description is None:
            continue

        # Generate the appropriate course object.
        departments[prefix.lower()].courses.append(Course(
            number=cnum,
            title=title,
            description=description))

    log.info( "Completed scraping." )

