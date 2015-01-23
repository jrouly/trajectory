"""
trajectory/scrape/engines/pdx_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to PDX's CS department.
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
            'name': "Portland State University",
            'abbrev': "PDX",
            'web': "pdx.edu",
        },
    ],
    'departments': [
        {
            'school': "Portland State University",
            'name': "Computer Science",
            'abbrev': "CS",
            'web': "pdx.edu/computer-science",
        },
        {
            'school': "Portland State University",
            'name': "Systems Science",
            'abbrev': "SYSC",
            'web': "pdx.edu/sysc",
        },
        {
            'school': "Portland State University",
            'name': "Electrical and Computer Engineering",
            'abbrev': "ECE",
            'web': "pdx.edu/ece",
        },
    ],
    'programs': [
        {
            'school': "Portland State University",
            'name': "PDX CS",
            'abbrev': "pdx_cs",
        },
    ],
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

    # Pregenerate SQL data.
    sql = ["INSERT INTO Courses (DepartmentID, Num, Title, Description) ",
            "VALUES "]
    course_sql = "('%(departmentID)s', '%(num)s', '%(title)s', '%(desc)s'), "
    departmentID_cs   = database.get_departmentID(args,
            school_name=META.get("departments")[0].get("school"),
            department_abbrev=META.get("departments")[0].get("abbrev"))
    departmentID_sysc = database.get_departmentID(args,
            school_name=META.get("departments")[1].get("school"),
            department_abbrev=META.get("departments")[1].get("abbrev"))
    departmentID_ece  = database.get_departmentID(args,
            school_name=META.get("departments")[2].get("school"),
            department_abbrev=META.get("departments")[2].get("abbrev"))


    for course in course_list:
        log.debug(course.text)
        full_title = re.compile("\s+").split(course.text)
        prefix = full_title[0]
        cnum = full_title[1]
        title = ' '.join(full_title[2:])

        description = ""

        # Select appropriate departmental ID
        if prefix == "CS":
            departmentID = departmentID_cs
        elif prefix == "ECE":
            departmentID = departmentID_ece
        elif prefix == "SYSC":
            departmentID = departmentID_sysc
        else:
            log.warn("Uknown course prefix " + full_title)
            continue

        # Interpolate the SQL query.
        sql.append(course_sql % {"departmentID": departmentID,
                                 "num": cnum,
                                 "title": title,
                                 "desc": description})

    # Generate the sql string.
    sql[-1] = sql[-1][:-2] # remove trailing comma
    sql.append(";")
    sql = "".join(sql)

    log.debug(sql)

    # Commit the sql query.
    c = args.db.cursor()
    c.executescript( sql )
    args.db.commit()

    log.info( "Completed scraping." )




    return

    # Identify the <UL> containing the course list by the H3 heading
    # "Course List" then find its first <UL> sibling.
    course_list_heading = index_soup.body.find("h3", text="Course List")
    course_list = course_list_heading.find_next_sibling("ul").findAll("a")


    # Loop over the list of courses in the <UL> we just found, access the
    # page they link to, and pull in their description and goals.
    log.debug( "Looping over course list." )
    for course in course_list:

        log.debug( "Course: " + course.text )

        # Identify the link to the course page and generate a BeautifulSoup
        # for the page contents.
        try:
            course_link = course.get("href")
            log.debug( "Getting: " + course_link )
            course_page = get( course_link )
            course_soup = BeautifulSoup( course_page.text )
            log.debug( "Soup generated." )

        except Exception as e:
            log.warning( "Error getting course page." )
            log.debug( course_link )
            log.debug( str(e) )
            exit( 3 )

        # Pull in course title as the name of this file.
        course_title = course_soup.find(id="page-title").text
        course_title = re.sub("/", "", course_title)
        log.debug( "Course title: " + course_title )

        # Identify the course table.
        course_table = course_soup.find("table")
        course_table_rows = course_table.findAll("tr")

        course_content = []

        # Iterate over course table rows.
        for row in course_table_rows:

            columns = row.findAll("td")

            # Skip any row without a key and value.
            if not len( columns ) == 2:
                continue

            # key is the first column, val is the second
            key = columns[0].text
            val = columns[1].text

            # Append value to the course_content list
            course_content.append( val )


        # Join together all the scraped text.
        course_content = ' '.join( course_content )

        # Output content to a .raw file.
        filename = course_title + ".raw"
        output_file = os.path.join( data_path, filename )
        with open( output_file, "w" ) as output:
            output.write( course_content )


    log.info( "Completed scraping." )

