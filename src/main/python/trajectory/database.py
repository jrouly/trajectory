"""
database.py
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
    log.info("Initializing database schema.")

    trj_home = os.environ.get("TRJ_HOME")
    sql_directory = os.path.join(trj_home, "src", "main", "resources", "sql")
    creation_script = os.path.join(sql_directory, "create_tables.sql")

    with open(creation_script, "r") as create_tables:
        sql = create_tables.read()
        c = args.db.cursor()
        c.executescript( sql )
        args.db.commit()


def register( args, metadata ):
    """
    Register a scrape target's metadata with the database. If an entry
    already exists for this target's defined data, update it.
    """

    import logging, os, sqlite3

    log = logging.getLogger("root")

    # Define SQL headers.
    school_sql = (
        "INSERT INTO 'Schools' ",
        "('Name', 'Abbreviation', 'Web')",
        "VALUES ",
    )
    department_sql = (
        "INSERT INTO 'Departments' ",
        "('SchoolID', 'Name', 'Abbreviation', 'Web')",
        "VALUES ",
    )
    program_sql = (
        "INSERT INTO 'Programs' ",
        "('SchoolID', 'Name', 'Abbreviation')""",
        """VALUES """,
    )
