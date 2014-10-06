"""
trajectory/scrapers/gmu/cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's CS department.
"""


from bs4 import BeautifulSoup
from werkzeug import url_fix
from urllib.parse import urljoin
from requests import get
from requests.exceptions import HTTPError
from datetime import datetime
import logging
import re
import os


def scrape( args ):
    """
    Scrape the available syllabi from the GMU CS page into a local
    directory.
    """

    # Set up logging utility.
    timestamp = datetime.strftime( datetime.now(), "%s" )
    logging.basicConfig(filename="../logs/output-%s.log" % timestamp, level=logging.DEBUG)
    logging.info( "Beginning." )

    # Hardcoded GMU CS syllabi repository
    url = "http://cs.gmu.edu"
    courses_url = "/courses/"

    # Hardcoded local data directory
    path = "../../data/gmu"

    # Create path if need be.
    if os.path.exists( path ):
        logging.info( "Data path %s exists already. Exiting." % path )
    else:
        logging.info( "Data path %s does not exist, creating." % path )
        os.makedirs( path )

    # Request index page and generate soup.
    try:
        index_link = urljoin( url, courses_url )
        index_link = url_fix( index_link )
        logging.debug( index_link )
        index_page = get( index_link )
        index_soup = BeautifulSoup( index_page.text )
    except Exception as e:
        logging.warning( "Error." )
        logging.debug( index_link )
        logging.debug( str(e) )
        exit( 2 )

    logging.info( "Generated index soup." )

    # Find the semester links.
    semester_tags = index_soup.find_all("a", href=re.compile("^/syllabus/.*$"))
    logging.info( "Grabbed semester list." )

    # Iterate over each semester.
    logging.info( "Begin scraping per semester." )
    for semester_tag in semester_tags:

        logging.debug("Semester: %s" % semester_tag.text)

        # Store semesters in a directory.
        semester_path = re.sub(r'\s+', ' ', semester_tag.text)
        semester_path = os.path.join( path, semester_path )
        if not os.path.exists( semester_tag.text ):
            os.makedirs( semester_path )

        # Request semester index page and generate soup.
        try:
            semester_link = urljoin( url, semester_tag['href'] )
            semester_link = url_fix( semester_link )
            semester_page = get( semester_link )
            semester_soup = BeautifulSoup( semester_page.text )
        except Exception:
            logging.warning( "Error." )
            logging.debug( semester_link )
            logging.debug( semester_tag.text )
            logging.debug( str(e) )
            continue

        # Find the syllabus links.
        syllabus_tags = semester_soup.find_all("a", text=re.compile("^\D{2,5}\s*\d{3}"))

        # Iterate over each syllabus.
        for syllabus_tag in syllabus_tags:

            logging.debug("Syllabus link: %s" % syllabus_tag['href'])

            # Request syllabus page.
            try:
                syllabus_link = urljoin( semester_link, syllabus_tag['href'] )
                syllabus_link = url_fix( syllabus_link )
                syllabus_page = get( syllabus_link )
            except Exception as e:
                logging.warning( "Error." )
                logging.debug( syllabus_link )
                logging.debug( syllabus_tag.text )
                logging.debug( str(e) )
                continue

            # Write syllabus to disk.
            syllabus_path = re.sub(r'\s+', ' ', syllabus_tag.text) + ".raw"
            syllabus_path = os.path.join( semester_path, syllabus_path )
            with open( syllabus_path, 'w' ) as syllabus:
                syllabus.write( syllabus_page.text )

    logging.info( "Completed scraping per semester." )






def clean( args ):
    """
    This function takes the gmu cs syllabi directory as input and removes
    all HTML entities and non-word elements from them.
    """

    timestamp = datetime.strftime( datetime.now(), "%s" )
    logging.basicConfig(level=logging.DEBUG)
    logging.info( "Beginning." )

    path = "../../data/gmu"
    whitespace = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W")
    singletons = re.compile("\s+\w(?=\s+)")
    long_whitespace = re.compile("\s+")

    # Generate a list of all data files in the data path.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( path )
             for name in files
             if name.endswith(".raw")]

    # Iterate over each datafile
    for datafile in files:

        logging.debug("Datafile: %s" % datafile)

        # Generate a soup object for each and strip it to its textual contents
        try:
            with open(datafile, 'r') as socket:
                soup = BeautifulSoup( socket )         # generate soup

            strings = soup.body.stripped_strings
            contents = ' '.join( strings )
        except:
            logging.warning( "Error detected in %s" % datafile )
            continue

        contents = re.sub(whitespace, ' ', contents) # remove non-letters
        contents = re.sub(singletons, ' ', contents) # remove single letters
        contents = re.sub(long_whitespace, ' ', contents)   # remove spaces
        contents = contents.lower()     # make everything lowercase

        # Write out to a new file
        with open( datafile[:-3] + "txt", 'w' ) as out:
            out.write( contents )

    logging.info( "Completed data processing." )
