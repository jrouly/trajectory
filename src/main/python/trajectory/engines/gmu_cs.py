"""
trajectory/engines/gmu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's CS department.
"""


from trajectory import database, clean
from bs4 import BeautifulSoup
from werkzeug import url_fix
from urllib.parse import urljoin
from requests.exceptions import HTTPError
import requests
import re
import os


# Constant values.
META = {
    'schools': [
        {
            'name': "George Mason University",
            'abbrev': "GMU",
            'web': "gmu.edu",
        },
    ],
    'departments': [
        {
            'school': "George Mason University",
            'name': "Computer Science",
            'abbrev': "CS",
            'web': "cs.gmu.edu",
        },
    ],
    'programs': [
        {
            'school': "George Mason University",
            'name': "GMU CS",
            'abbrev': "gmu_cs",
        },
    ],
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

    # Pregenerate SQL data.
    sql = ["INSERT INTO Courses (DepartmentID, Num, Title, Description) ",
            "VALUES "]
    course_sql = "('%(departmentID)s', '%(num)s', '%(title)s', '%(desc)s'), "
    departmentID = database.get_departmentID(args,
            school_name=META.get("departments")[0].get("school"),
            department_name=META.get("departments")[0].get("name"))

    # Identify relevant information for each course.
    for course in course_list:

        # Generate metadata
        log.debug(course.text)
        full_title = re.compile("\s+").split(course.text)
        prefix = full_title[0]
        cnum = full_title[1]
        title = ' '.join(full_title[3:])

        # Identify coid to get description.
        onclick = course['onclick']
        (catid, coid) = re.sub( catid_re, "", onclick ).split(", ")

        # Generate a BeautifulSoup object of the course description.
        course_page = requests.get( course_url % (catid, coid) )
        course_soup = BeautifulSoup( course_page.text )
        content = course_soup.find(class_="block_content_popup").hr.text

        # Clean up the description.
        description = str.replace(content, "'", "") # strip quotes
        try:
            description = description[:description.index("Hours of Lecture")]
        except:
            pass

        # Identify prerequisites
        prereq_index = description.find("Prerequisite(s)")
        if prereq_index > -1:
            prereq_string = description[prereq_index:]
            description = description[:prereq_index]
            log.debug(prereq_string)

        # Clean the description string
        description = clean(args, description)
        if description is None:
            continue

        # Interpolate the SQL query.
        sql.append( course_sql % {"departmentID": departmentID,
                                  "num": cnum,
                                  "title": title,
                                  "desc": description} )

    # Generate the sql string.
    sql[-1] = sql[-1][:-2] # remove trailing comma
    sql.append(";")
    sql = "".join(sql)

    # Commit the sql query.
    c = args.db.cursor()
    c.executescript( sql )
    args.db.commit()

    log.info( "Completed scraping." )

