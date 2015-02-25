"""
trajectory/engines/gmu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's CS department.
"""


from trajectory.models import University, Department, Course
from trajectory.core import clean
from bs4 import BeautifulSoup
import requests
import re
import os


# Constant values.
META = {
    'school': {
        'name': "George Mason University",
        'abbreviation': "GMU",
        'url': "gmu.edu",
        },
    'departments': [
        {
            'name': "Computer Science",
            'abbreviation': "CS",
            'url': "cs.gmu.edu",
        },
        {
            'name': "Electrical and Computer Engineering",
            'abbreviation': "ECE",
            'url': "ece.gmu.edu",
        },
    ]
}


def scrape(args):
    """
    Scrape the available syllabi from the GMU CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping GMU CS data." )


    # Generate a BeautifulSoup object.
    catalog_index_url = "http://catalog.gmu.edu/preview_course_incoming.php?cattype=combined&prefix=cs"
    catalog_index = requests.get( catalog_index_url )
    soup = BeautifulSoup( catalog_index.text )

    # Identify the list of courses.
    course_list = soup.find_all(
            name="a",
            onclick=re.compile("showCourse.*"))

    # Select only the catid and coid.
    catid_re = re.compile("(^[^']*)|(, this.*$)|(')")

    # Piecewise course page url.
    course_url = "http://catalog.gmu.edu/preview_course.php?catoid=%s&coid=%s"

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
        title = ' '.join(full_title[3:])

        # Identify coid to get description.
        onclick = course['onclick']
        (catid, coid) = re.sub(catid_re, "", onclick).split(", ")

        # Generate a BeautifulSoup object of the course description.
        course_page = requests.get(course_url % (catid, coid))
        course_soup = BeautifulSoup(course_page.text)
        content = course_soup.find(class_="block_content_popup").hr.text

        # Clean up the description.
        description = content
        try:
            description = description[:description.index("Hours of Lecture")]
        except:
            pass

        # Identify prerequisites
        # TODO: Match these up with their database entries.
        prereq_index = description.find("Prerequisite(s)")
        if prereq_index > -1:
            prereq_string = description[prereq_index:]
            description = description[:prereq_index]

            prereq_re = re.compile("\w{2,4}\s\d{3}")
            matches = re.findall(prereq_re, prereq_string)
            if len(matches) > 0:
                prereqs["%s %s" % (prefix, cnum)] = matches

        # Clean the description string
        description = clean(args, description)
        if description is None:
            continue

        # Generate the appropriate course object.
        departments[prefix.lower()].courses.append(Course(
            number=cnum,
            title=title,
            description=description))

    log.info( "Completed scraping." )

