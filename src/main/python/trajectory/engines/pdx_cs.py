"""
trajectory/scrape/engines/pdx_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to PDX's CS department.
"""


from bs4 import BeautifulSoup
from werkzeug import url_fix
from urllib.parse import urljoin
from requests import get
from requests.exceptions import HTTPError
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
    ],
    'programs': [
        {
            'school': "Portland State University",
            'name': "PDX CS",
            'abbrev': "pdx_cs",
        },
    ],
}


def scrape( args, data_path ):
    """
    Scrape the available syllabi from the PDX CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping PDX CS data." )


    # PDX CS syllabi repository
    url = "http://www.pdx.edu/computer-science/"
    courses_url = "courses"


    # Request index page and generate soup.
    try:
        index_link = urljoin( url, courses_url )
        index_link = url_fix( index_link )
        log.debug( "Getting index: " + index_link )
        index_page = get( index_link )
        index_soup = BeautifulSoup( index_page.text )

    except Exception as e:
        log.warning( "Error." )
        log.debug( index_link )
        log.debug( str(e) )
        exit( 2 )


    log.debug( "Generated index soup." )


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



def clean( args, raw_path, clean_path ):
    """
    This function takes the pdx cs syllabi directory as input and removes
    all non-word elements from them.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Cleaning scraped PDX CS data." )


    whitespace = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W")
    singletons = re.compile("\s+\w{1,3}(?=\s+)")
    long_whitespace = re.compile("\s+")

    # Generate a list of all data files in the data path.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( raw_path )
             for name in files
             if name.endswith(".raw")]

    # Iterate over each raw file
    for raw_file in files:

        with open(raw_file, 'r') as socket:
            contents = socket.read()

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

        filename = os.path.basename( raw_file )[:-3] + "txt"
        clean_file = os.path.join( clean_path, filename )

        # Write out to a new file.
        with open( clean_file, 'w' ) as out:
            out.write( contents )

    log.info( "Completed data processing." )
