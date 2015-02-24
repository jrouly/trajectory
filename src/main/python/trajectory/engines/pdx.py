"""
trajectory/scrape/engines/pdx_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to PDX's CS department.
"""


from trajectory.models import University, Course, Department
from trajectory import clean
from bs4 import BeautifulSoup
import requests
import re
import os


# Constant values.
META = {
    'school': {
        'name': "Portland State University",
        'abbreviation': "PDX",
        'url': "pdx.edu",
    },
    'departments': [
        {
            'name': "Computer Science",
            'abbreviation': "CS",
            'url': "pdx.edu/computer-science",
        },
        {
            'name': "Systems Science",
            'abbreviation': "SYSC",
            'url': "pdx.edu/sysc",
        },
        {
            'name': "Electrical and Computer Engineering",
            'abbreviation': "ECE",
            'url': "pdx.edu/ece",
        }
    ]
}


def scrape(args):
    """
    Scrape the available syllabi from the PDX CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping PDX CS data." )


    # Construct a soup of the index.
    course_index_url = "http://www.pdx.edu/computer-science/courses"
    course_index = requests.get(course_index_url)
    soup = BeautifulSoup(course_index.text)

    # Identify the list of courses.
    course_list = soup.find("h3", text="Course List")\
                      .find_next_sibling("ul")\
                      .find_all("a")

    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = args.session.query(University)\
            .filter(University.name==university)\
            .first()
    departments = {department.abbreviation.lower() : department
                    for department in args.session.query(Department)\
                        .filter(Department.university==university)\
                        .all()}

    for course in course_list:
        log.debug(course.text)
        full_title = re.compile("\s+").split(course.text)
        prefix = full_title[0]
        cnum = full_title[1]
        title = ' '.join(full_title[2:])

        try:
            course_url = course['href']
            course_soup = BeautifulSoup(requests.get(course_url).text)
        except:
            log.warn("Unable to parse course page.")
            log.warn(course_url)
            continue

        # Find the course description based on its neighbour
        cdesc_re = re.compile(".*Course Description.*")
        cdesc = course_soup.find("table").find(text=cdesc_re)
        if not cdesc.next_sibling:
            cdesc = cdesc.find_parent("td")

        # If there's no course description found, well, forget it
        try:
            description = cdesc.find_next_sibling("td").text
        except:
            log.warn("No course description available.")
            log.warn(course_url)
            continue

        # Clean the description string.
        description = clean(args, description)
        if description is None:
            continue

        # Find the course prerequisite list based on its neighbour
        prereq_re = re.compile(".*Prerequi?sites.*")
        prereq = course_soup.find("table").find(text=prereq_re)
        if not prereq.next_sibling:
            prereq = prereq.find_parent("td")

        # If there's no prereq list found, leave it as None
        try:
            prereq = prereq.find_next_sibling("td").text
        except:
            prereq = None

        # Generate the appropriate course object.
        departments[prefix.lower()].courses.append(Course(
            number=cnum,
            title=title,
            description=description))

    log.info( "Completed scraping." )

