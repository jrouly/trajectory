"""
clean.py
Author: Jean Michel Rouly

This file takes the gmu cs syllabi directory as input and removes all HTML
entities and non-word elements from them.
"""


from bs4 import BeautifulSoup
from datetime import datetime

import logging
import os
import re

def main():

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



if __name__ == '__main__':
    main()
