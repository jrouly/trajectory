"""
trajectory/engines/rpi_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to RPI's CS department.
"""


from trajectory import database, clean
from bs4 import BeautifulSoup
import requests
import re
import os


# Constant values.
META = {
    'schools': [
        {
            'name': "Rensselaer Polytechnic Institute",
            'abbrev': "RPI",
            'web': "rpi.edu",
        },
    ],
    'departments': [
        {
            'school': "Rensselaer Polytechnic Institute",
            'name': "Computer Science",
            'abbrev': "CSCI",
            'web': "cs.rpi.edu",
        },
    ],
    'programs': [
        {
            'school': "Rensselaer Polytechnic Institute",
            'name': "RPI CS",
            'abbrev': "rpi_cs",
        },
    ],
}


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

    # Pregenerate SQL data.
    sql = ["INSERT INTO Courses (DepartmentID, Num, Title, Description) ",
            "VALUES "]
    course_sql = "('%(departmentID)s', '%(num)s', '%(title)s', '%(desc)s'), "
    departmentID = database.get_departmentID(args,
            school_name=META.get("departments")[0].get("school"),
            department_abbrev=META.get("departments")[0].get("abbrev"))

    if departmentID is None:
        log.warn("No valid Department ID found, ensure target is registered.")
        return

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

