"""
trajectory/scrape/engines/gmu_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's CS department.
"""


from bs4 import BeautifulSoup
from werkzeug import url_fix
from urllib.parse import urljoin
from requests import get
from requests.exceptions import HTTPError
import re
import os


import logging
log = logging.getLogger("root")


# Constant values.

# GMU CS syllabi repository
url = "http://cs.gmu.edu"
courses_url = "/courses/"
syllabus_url_regex = re.compile("^/syllabus/.*$")
data_id = "gmu_cs"


def scrape( args, data_path ):
    """
    Scrape the available syllabi from the GMU CS page into a local
    directory.
    """


    log.info( "Scraping GMU CS data." )


    # Request index page and generate soup.
    try:
        index_link = urljoin( url, courses_url )
        index_link = url_fix( index_link )
        log.debug( index_link )
        index_page = get( index_link )
        index_soup = BeautifulSoup( index_page.text )

    except Exception as e:
        log.warning( "Error." )
        log.debug( index_link )
        log.debug( str(e) )
        exit( 2 )

    log.debug( "Generated index soup." )

    # Find the semester links.
    semester_tags = index_soup.find_all("a", href=syllabus_url_regex)
    log.debug( "Grabbed semester list." )

    # Iterate over each semester.
    log.debug( "Begin scraping per semester." )
    for semester_tag in semester_tags:

        log.debug("Semester: %s" % semester_tag.text)

        # Store semesters in a directory.
        semester_path = re.sub(r'\s+', ' ', semester_tag.text)
        semester_path = os.path.join( data_path, semester_path )
        if not os.path.exists( semester_tag.text ):
            os.makedirs( semester_path )

        # Request semester index page and generate soup.
        try:
            semester_link = urljoin( url, semester_tag['href'] )
            semester_link = url_fix( semester_link )
            semester_page = get( semester_link )
            semester_soup = BeautifulSoup( semester_page.text )
        except Exception:
            log.warning( "Error." )
            log.debug( semester_link )
            log.debug( semester_tag.text )
            log.debug( str(e) )
            continue

        # Find the syllabus links.
        syllabus_tags = semester_soup.find_all("a", text=re.compile("^\D{2,5}\s*\d{3}"))

        # Iterate over each syllabus.
        for syllabus_tag in syllabus_tags:

            log.debug("Syllabus link: %s" % syllabus_tag['href'])

            # Request syllabus page.
            try:
                syllabus_link = urljoin( semester_link, syllabus_tag['href'] )
                syllabus_link = url_fix( syllabus_link )
                syllabus_page = get( syllabus_link )
            except Exception as e:
                log.warning( "Error." )
                log.debug( syllabus_link )
                log.debug( syllabus_tag.text )
                log.debug( str(e) )
                continue

            # Write syllabus to disk.
            syllabus_path = re.sub(r'\s+', ' ', syllabus_tag.text) + ".raw"
            syllabus_path = os.path.join( semester_path, syllabus_path )
            with open( syllabus_path, 'w' ) as syllabus:
                syllabus.write( syllabus_page.text )

    log.info( "Completed scraping." )



def clean( args, data_path ):
    """
    This function takes the gmu cs syllabi directory as input and removes
    all HTML entities and non-word elements from them.
    """

    log.info( "Cleaning scraped GMU CS data." )
    return


    whitespace = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W")
    singletons = re.compile("\s+\w{1,3}(?=\s+)")
    long_whitespace = re.compile("\s+")

    # Generate a list of all data files in the data path.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( data_path )
             for name in files
             if name.endswith(".raw")]

    # Iterate over each datafile
    for datafile in files:

        log.debug("Datafile: %s" % datafile)

        # Generate a soup object for each and strip it to its textual contents
        try:
            with open(datafile, 'r') as socket:
                soup = BeautifulSoup( socket )         # generate soup

            strings = soup.body.stripped_strings
            contents = ' '.join( strings )
        except:
            log.warning( "Error detected in %s" % datafile )
            continue

        contents = re.sub(whitespace, ' ', contents) # remove non-letters
        contents = re.sub(singletons, ' ', contents) # remove 1-2 letter words
        contents = re.sub(long_whitespace, ' ', contents)   # remove spaces
        contents = contents.lower()     # make everything lowercase

        # Write out to a new file
        with open( datafile[:-3] + "txt", 'w' ) as out:
            out.write( contents )

    log.info( "Completed data processing." )
