"""
database/__init__.py
Author: Jean Michel Rouly

This module defines a number of database maintenance and creation
functions. The schema is laid out in these functions.
"""


def initialize( args ):
    """
    If it doesn't exist, create the database. Initialize all tables.
    """


    import logging, os, sqlite3


    log = logging.getLogger("root")
    log.info("Initializing SQLite database.")


    pass


def populate( args ):
    """
    Populate all known values in the database.
    """

    import logging, os, sqlite3


    log = logging.getLogger("root")
    log.info("Initializing SQLite database.")


    pass

