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


def register_target( args, metadata ):
    """
    Register a scrape target's metadata with the database. If an entry
    already exists for this target's defined data, update it.
    """

    import logging, os, sqlite3

    log = logging.getLogger("root")

    # Define SQL headers.
    school_sql = [
        "INSERT INTO 'Schools' ",
        "('Name', 'Abbreviation', 'Web') ",
        "VALUES ",
    ]
    department_sql = [
        "INSERT INTO 'Departments' ",
        "('SchoolID', 'Name', 'Abbreviation', 'Web') ",
        "VALUES ",
    ]
    program_sql = [
        "INSERT INTO 'Programs' ",
        "('SchoolID', 'Name', 'Abbreviation') ",
        "VALUES ",
    ]

    # Get a database cursor.
    c = args.db.cursor()

    # Grab data from metadata object.
    schools = metadata.get("schools")
    departments = metadata.get("departments")
    programs = metadata.get("programs")

    # Loop through schools, registering entries.
    for school in schools:
        value = "('%(name)s', '%(abbrev)s', '%(web)s'), "
        school_sql.append(value % school)
    school_sql[-1] = school_sql[-1][:-2] # remove trailing comma
    school_sql.append(";")
    school_sql = ''.join(school_sql)

    c.executescript( school_sql )
    args.db.commit()

    # Loop through departments, registering entries.
    for department in departments:
        schoolname = department.get("school")
        department["schoolid"] = get_schoolID(args, schoolname)
        value = "('%(schoolid)s', '%(name)s', '%(abbrev)s', '%(web)s'), "
        department_sql.append(value % department)
    department_sql[-1] = department_sql[-1][:-2] # remove trailing comma
    department_sql.append(";")
    department_sql = ''.join(department_sql)

    c.executescript( department_sql )
    args.db.commit()

    # Loop through programs, registering entries.
    for program in programs:
        schoolname = program.get("school")
        program["schoolid"] = get_schoolID(args, schoolname)
        value = "('%(schoolid)s', '%(name)s', '%(abbrev)s'), "
        program_sql.append(value % program)
    program_sql[-1] = program_sql[-1][:-2] # remove trailing comma
    program_sql.append(";")
    program_sql = ''.join(program_sql)

    c.executescript( program_sql )
    args.db.commit()


def get_schoolID( args, name ):
    """
    Lookup the ID of a School by its name.
    """

    c = args.db.cursor()
    c.execute("SELECT S.ID FROM Schools S WHERE S.Name='%s';" % name)

    try:
        return c.fetchone()[0]
    except:
        return None


def get_departmentID( args, school_name, department_name ):
    """
    Lookup the ID of a Department by its name and the name of its
    associated school.
    """

    c = args.db.cursor()
    c.execute("""SELECT D.ID
                 FROM Schools S, Departments D
                 WHERE S.Name='%s'
                   AND D.Name='%s'
                   AND D.SchoolID=S.ID;""" % (school_name, department_name) )

    try:
        return c.fetchone()[0]
    except:
        return None
