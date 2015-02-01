"""
trajectory/engines/stanford_cs.py
Author: Jean Michel Rouly

This file is the scraping engine tooled to Stanford's CS department.
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
            'name': "Stanford University",
            'abbrev': "Stanford",
            'web': "stanford.edu",
        },
    ],
    'departments': [
        {
            'school': "Stanford University",
            'name':
            "Compuhttp://catalog.gmu.edu/preview_course_incoming.php?cattype=combined&prefix=c://explorecourses.stanford.edu/search?q=CS&view=catalog&filter-departmentcode-CS=on&filter-term-Spring=on&page=0&filter-coursestatus-Active=onter Science",
            'abbrev': "CS",
            'web': "cs.stanford.edu",
        },
    ],
    'programs': [
        {
            'school': "Stanford",
            'name': "Stanford CS",
            'abbrev': "stanford_cs",
        },
    ],
}


def scrape(args):
    """
    Scrape the available syllabi from the Stanford CS page into a local
    directory.
    """


    import logging
    log = logging.getLogger("root")
    log.info( "Scraping Stanford CS data." )


    # Generate a BeautifulSoup object.
    catalog_index_url = "https://explorecourses.stanford.edu/search?q=CS&view=catalog&filter-departmentcode-CS=on&filter-term-Spring=on&page=0&filter-coursestatus-Active=on"
    catalog_index = requests.get( catalog_index_url )
    soup = BeautifulSoup( catalog_index.text )


    log.info( "Completed scraping." )

