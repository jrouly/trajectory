"""
trajectory/scrape/engines/pdx_chem.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to PDX's Chemistry department.
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

# PDX CS syllabi repository
url = "http://www.pdx.edu/chem/syllabi-archives"
courses_url = "courses"


def scrape( args, data_path ):
    """
    Scrape the available syllabi from the PDX Chemistry page into a local
    directory.
    """


    log.info( "Scraping PDX Chemistry data." )


    # Request index page and generate soup.
    try:
        index_link = url_fix( url )
        log.debug( "Getting index: " + index_link )
        index_page = get( index_link )
        index_soup = BeautifulSoup( index_page.text )

    except Exception as e:
        log.warning( "Error." )
        log.debug( index_link )
        log.debug( str(e) )
        exit( 2 )


    log.debug( "Generated index soup." )


    # Identify the list of <a> tags containing download links.
    course_list = index_soup.findAll("a", text="Download")


    # Loop over the list of courses and download the PDF they link to.
    log.debug( "Looping over course list." )
    for course in course_list:

        syllabus_link = course.get("href")
        if syllabus_link is None:
            log.debug("Syllabus link not found.")
            continue

        syllabus_link = url_fix( syllabus_link )
        log.debug( "Course URL: " + syllabus_link )

        try:
            syllabus = get( syllabus_link, stream=True )
        except Exception:
            # Something went wrong
            log.debug("Invalid URL.")
            continue

        if not syllabus.ok:
            # Something went wrong
            log.debug("Error downloading syllabus.")
            continue

        # Write syllabus to disk.
        syllabus_path = syllabus_link.split('/')[-1]
        syllabus_path = os.path.join( data_path, syllabus_path )

        with open( syllabus_path, 'wb' ) as handle:
            for block in syllabus.iter_content(1024):
                if not block:
                    break
                handle.write( block )

    log.info( "Completed scraping." )



def clean( args, raw_path, clean_path ):
    """
    This function takes the pdx chem syllabi directory as input and removes
    all non-word elements from them.
    """


    log.info( "Cleaning scraped PDX Chemistry data." )


    # Generate a list of all pdf data files in the data path.
    pdfs = [os.path.join(root, name)
             for root, dirs, files in os.walk( raw_path )
             for name in files
             if name.endswith(".pdf")]

    # Convert PDFs to text.
    log.info( "Convert PDFs to text." )
    from subprocess import call
    try:
        for pdf in pdfs:
            filename = os.path.basename( pdf )[:-3] + "txt"
            clean_file = os.path.join( clean_path, filename )
            call(["pdftotext", pdf, clean_file])
    except Exception as e:
        log.error( "Unable to call system 'pdftotext' command." )
        log.error( str(e) )


    # Generate a list of the newly generated text files.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( clean_path )
             for name in files
             if name.endswith(".txt")]


    # Define cleaning regular expressions.
    whitespace = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W")
    singletons = re.compile("\s+\w{1,3}(?=\s+)")
    long_whitespace = re.compile("\s+")


    # Iterate over each datafile
    log.info( "Clean up text files." )
    for datafile in files:

        with open( datafile, "r" ) as content_file:
            contents = content_file.read()


        # Perform regular expression substitutions.
        contents = re.sub(whitespace, ' ', contents) # remove non-letters
        contents = re.sub(singletons, ' ', contents) # remove single letters
        contents = re.sub(long_whitespace, ' ', contents)   # remove spaces
        contents = contents.lower()     # make everything lowercase


        # Trim syllabi with fewer than 500 characters, as they likely were
        # incorrectly cleaned.
        if len( contents ) <= 500:
            log.debug("File contents too short, skipping.")
            os.remove( datafile )
            continue

        # Write out to the same file.
        with open( datafile, 'w' ) as out:
            out.write( contents )

    log.info( "Completed data processing." )
