"""
trajectory/engines/stanford_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to Stanford's CS department.
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
        'name': "Stanford University",
        'abbreviation': "Stanford",
        'url': "stanford.edu",
    },
    'departments': [
        {
            'name': "Computer Science",
            'abbreviation': "CS",
            'url': "cs.stanford.edu",
        },
    ]
}


def scrape(args):
    """
    Scrape the available syllabi from the Stanford CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info("Scraping Stanford CS data.")


    # Fetch existing metadata objects from database.
    university = META.get("school").get("name")
    university = args.session.query(University)\
            .filter(University.name==university)\
            .first()
    departments = {department.abbreviation.lower() : department
                    for department in args.session.query(Department)\
                        .filter(Department.university==university)\
                        .all()}


    # Static connection information
    catalog_url = "https://explorecourses.stanford.edu/search?q=CS&view=catalog&filter-departmentcode-CS=on&filter-term-Spring=on&filter-coursestatus-Active=on&page="
    catalog_page = 0
    catalog_page_limit = 8
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36\
            (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    }


    # Loop forever until we get to the last page and can't "next >" any
    # more, in which case we stop.
    while True:

        # There are currently only 8 pages, so break after we see that
        # many.
        if catalog_page == catalog_page_limit:
            break

        # Generate a BeautifulSoup object.
        response = requests.get(catalog_url + str(catalog_page),
                                headers=headers)
        soup = BeautifulSoup(response.text)

        # Identify the course list.
        course_list = soup.find_all(class_="searchResult")

        # Identify relevant information for each course.
        for course in course_list:

            # Generate metadata
            title = course.find(class_="courseTitle").text
            identifier = re.compile("\s+").split(
                    course.find(class_="courseNumber").text)
            prefix = identifier[0]
            cnum = identifier[1][:-1]
            description = course.find(class_="courseDescription").text

            log.debug(identifier)

            # Identify prerequisites or corequisites.
            # TODO: Match these up with their database entries.
            prereq_index = description.find("Prerequisite")
            if prereq_index > -1:
                prereq_string = description[prereq_index:]
                description = description[:prereq_index]

            # Clean the description string
            description = clean(args, description)
            if description is None:
                continue

            # Generate the appropriate course object.
            departments[prefix.lower()].courses.append(Course(
                number=cnum,
                title=title,
                description=description))

        # Go to the next page.
        catalog_page = catalog_page + 1


    log.info( "Completed scraping." )

