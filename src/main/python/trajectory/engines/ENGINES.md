# Scraping Engines

A scraping engine is a pluggable Python module that generates data by
downloading documents from the Internet. Specifically, each engine
"targets" a university's program of study and downloads course
descriptions. The scraping process includes downloading the data into a
temporary directory and then cleaning it of any noise, and finally
inserting it into a metadata-aware database.

## Basic Interface

Every engine needs to implement a simple interface to support pluggability.

#### Metadata Object

The metadata object `META` is a simple Python dictionary of the following
structure:

    META = {
        'school': {
            'name': "Example University",
            'abbreviation': "EU",
            'url': "example.edu",
            },
        'departments': [
            {
                'name': "Sample Department",
                'abbreviation': "SD",
                'url': "sample.example.edu",
            },
        ]
    }

Multiple programs, departments, and schools can be specified in a single
metadata object. Only those programs, departments, and schools which will
be involved in the scraping process should be defined in a single engine,
though.

#### Scrape Function

The scrape function expects a simple header

    def scrape(args):
        pass

`args` is the Trj configuration object. The purpose of this function
is to download all available content from a course description repository
into a temporary holding directory (if necessary), clean the textual data,
and insert it in the correct location in the database layer.
