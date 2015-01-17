"""
trajectory/engines/gmu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's CS department.
"""


from trajectory import database
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
        # TODO strip out prerequisite courses here
        prereq_index = description.find("Prerequisite(s)")
        if prereq_index > -1:
            pass

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



def clean( args, data_path ):
    """
    This function takes the gmu cs syllabi directory as input and removes
    all HTML entities and non-word elements from them.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Cleaning scraped GMU CS data." )


    # Look up database IDs for this target's schools & departments.
    schoolIDs = []
    for school in META.get("schools"):
        schoolname = school.get("name")
        schoolIDs.append( database.get_schoolID( args, schoolname ) )

    departmentIDs = []
    for department in META.get("departments"):
        departmentname = department.get("name")
        schoolname = department.get("school")
        departmentIDs.append(
            database.get_departmentID( args, schoolname, departmentname ) )


    whitespace = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W")
    singletons = re.compile("\s+\w{1,3}(?=\s+)")
    long_whitespace = re.compile("\s+")

    # Generate a list of all data files in the data path.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( data_path )
             for name in files
             if name.endswith(".raw")]

    # Iterate over each raw file
    for raw_file in files:

        #log.debug("Raw file: %s" % raw_file)

        # Generate a soup object for each and strip it to its textual contents
        try:
            with open(raw_file, 'r') as socket:
                soup = BeautifulSoup( socket )         # generate soup

            strings = soup.body.stripped_strings
            contents = ' '.join( strings )
        except:
            log.warning( "Error detected in %s" % raw_file )
            continue

        # Perform regular expression substitutions.
        contents = re.sub(whitespace, ' ', contents) # remove non-letters
        contents = re.sub(singletons, ' ', contents) # remove 1-2 letter words
        contents = re.sub(long_whitespace, ' ', contents)   # remove spaces
        contents = contents.lower()     # make everything lowercase

        # Trim syllabi with fewer than 500 characters, as they likely were
        # incorrectly cleaned.
        if len( contents ) < 500:
            log.debug("File contents too short, skipping.")
            continue

        # Create a new file path in the clean directory.
        semester = os.path.split( os.path.dirname( raw_file ) )[-1]
        output_filename = os.path.basename( raw_file )[:-3] + "txt"

        clean_semester = os.path.join( clean_path, semester )
        clean_file = os.path.join( clean_semester, output_filename )

        # Ensure that the semester path exists in the clean directory.
        if not os.path.exists( clean_semester ):
            os.makedirs( clean_semester )

        #log.debug( "clean_file: %s" % clean_file )

        # Write out to a new file.
        with open( clean_file, 'w' ) as out:
            out.write( contents )

    log.info( "Completed data processing." )
