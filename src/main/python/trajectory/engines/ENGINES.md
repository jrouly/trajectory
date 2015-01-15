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
        'schools': [
            {
                'name': "Example University",
                'abbrev': "EU",
                'web': "example.edu",
            },
        ],
        'departments': [
            {
                'school': "Example University",
                'name': "Sample Department",
                'abbrev': "SD",
                'web': "sample.example.edu",
            },
        ],
        'programs': [
            {
                'school': "Example University",
                'name': "EU SD",
                'abbrev': "eu_sd",
            },
        ],
    }

Multiple programs, departments, and schools can be specified in a single
metadata object. Only those programs, departments, and schools which will
be involved in the scraping process should be defined in a single engine,
though.

#### Scrape Function

The scrape function expects a simple header

    def scrape( args, data_path ):
        pass

`args` is the Trj configuration object. `data_path` is the temporary
directory intended to house raw download data. The purpose of this function
is to download all available content from a course description repository
into a temporary holding directory.

#### Clean Function

The clean function expects the header

    def clean( args, raw_path, clean_path ):
        pass

`args` is the Trj configuration object. `raw_path` is the temporary
directory holding the downloaded raw data from `scrape`. `clean_path` is
the output directory for all cleaned (digested) course descriptions.
