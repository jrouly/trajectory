"""
trajectory/scrape/engines/gmu_stat.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to GMU's statistics department.
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

# GMU Stat syllabi repository
url = "http://statistics.gmu.edu/courses/"
syllabus_url = "syllabus_archive_master.html"
syllabus_url_regex = re.compile("^syllabi/.*$")
data_id = "gmu_stat"


def scrape( args, data_path ):
    """
    Scrape the available syllabi from the GMU STAT page into a local
    directory.
    """


    log.info( "Scraping GMU STAT data." )


    # Request index page and generate soup.
    log.info("Begin downloading.")
    try:
        index_link = urljoin( url, syllabus_url )
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

    # Find the syllabus links.
    syllabus_tags = index_soup.find_all("a", href=syllabus_url_regex)
    log.debug( "Grabbed syllabus list." )

    # Iterate.
    log.debug( "Begin scraping syllabi." )
    for syllabus_tag in syllabus_tags:

        # Generate the url for the syllabus and download it.
        syllabus_link = urljoin( url, syllabus_tag.get("href"))
        syllabus_link = url_fix( syllabus_link )
        log.debug( syllabus_link )
        syllabus = get( syllabus_link, stream=True )

        if not syllabus.ok:
            # Something went wrong
            continue

        # Write syllabus to disk.
        syllabus_path = syllabus_tag.text
        syllabus_path = os.path.join( data_path, syllabus_path )
        with open( syllabus_path, 'wb' ) as handle:
            for block in syllabus.iter_content(1024):
                if not block:
                    break
                handle.write( block )


    log.info( "Completed scraping." )



def clean( args, data_path ):
    """
    This function takes the gmu cs syllabi directory as input and removes
    all HTML entities and non-word elements from them.
    """


    log.info( "Cleaning GMU STAT data." )


    # Generate a list of all pdf data files in the data path.
    pdfs = [os.path.join(root, name)
             for root, dirs, files in os.walk( data_path )
             for name in files
             if name.endswith(".pdf")]

    # Convert PDFs to text.
    log.info( "Convert PDFs to text." )
    from subprocess import call
    for pdf in pdfs:
        call(["pdftotext", pdf])


    # Generate a list of all doc data files in the data path.
    docs = [os.path.join(root, name)
             for root, dirs, files in os.walk( data_path )
             for name in files
             if name.endswith(".doc")]

    # Convert PDFs to text.
    log.info( "Convert DOCs to text." )
    from subprocess import call
    for doc in docs:
        with open("%s.txt"%doc,"w") as docout:
            call(["catdoc", doc], stdout=docout)


    # Generate a list of the new text files.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( data_path )
             for name in files
             if name.endswith(".txt")]

    whitespace = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W")
    singletons = re.compile("\s+\w{1,3}(?=\s+)")
    long_whitespace = re.compile("\s+")

    # Iterate over each datafile
    log.info( "Clean up text files." )
    for datafile in files:

        with open( datafile, "r" ) as content_file:
            contents = content_file.read()

        if len( contents ) <= 10:
            log.debug("File too short.")
            os.remove( datafile )
            continue

        contents = re.sub(whitespace, ' ', contents) # remove non-letters
        contents = re.sub(singletons, ' ', contents) # remove single letters
        contents = re.sub(long_whitespace, ' ', contents)   # remove spaces
        contents = contents.lower()     # make everything lowercase

        # Write out to a new file
        with open( datafile, 'w' ) as out:
            out.write( contents )

    log.info( "Completed data processing." )
