"""
trajectory/core.py
Author: Jean Michel Rouly

Define the core functionality of the Trajectory package, including modular
engine routing and text cleaning.
"""


def scrape(args):
    """
    Routes scraping to the appropriate scraper module.
    """

    from trajectory.models import University, Department, Course

    import logging
    import os
    from importlib import import_module

    log = logging.getLogger("root")
    log.info("Selected scraping targets: %s." % args.targets)

    # Loop over the requested targets and call their scrape function.
    for target in args.targets:

        log.info("Engaging scraper engine: %s" % target)

        # Prepend the target name with a dot for importing.
        target_module = ".%s" % target
        scraper = import_module( target_module, "trajectory.engines" )

        # Register the target with the database, if not already present.
        try:
            metadata = scraper.META

            university = metadata.get("school")
            university_query = args.session.query(University)\
                    .filter(University.name==university.get("name"))

            # If the university has already been registered, alert the user
            # but grab a reference to it for the Departments.
            if(university_query.count() > 0):
                university = university_query.first()
                log.warn("University '%s' already registered." % \
                        university.name)

            # If the university has not been registered, register a new
            # one.
            else:
                log.info("Registering university '%s' with database." % \
                        university.get("name"))
                university = University(
                        name=university.get("name"),
                        abbreviation=university.get("abbreviation"),
                        url=university.get("url"))

                # Add the university to the session.
                args.session.add(university)

            # Loop over the departments defined in the metadata.
            departments = metadata.get("departments")
            for department in departments:
                department_query = args.session.query(Department)\
                        .join(University)\
                        .filter(Department.name==department.get("name"))\
                        .filter(Department.university_id==university.id)

                # If the department has been registered, alert the user.
                if department_query.count() > 0:
                    log.warn("Department '%s' already registered." % \
                            department.get("name"))
                    continue

                # Otherwise register a new one.
                else:
                    university.departments.append(Department(
                            name=department.get("name"),
                            abbreviation=department.get("abbreviation"),
                            url=department.get("url")))
                    log.info("Registering department '%s' with database." % \
                            department.get("name"))

        except AttributeError as e:
            log.warn("Target %s metadata not defined." % target)
            log.warn("Terminating engine.")
            log.debug(e)
            continue

        # Begin downloading course data.
        try:

            # Check if there are already courses defined for any
            # departments within this university. If there are, skip
            # this target.
            if args.session.query(Course).join(Department) \
                    .filter(Course.department_id==Department.id)\
                    .filter(Department.university==university)\
                    .count() > 0:
                log.warn("Target %s already has courses defined." % target)

            # Otherwise, go ahead and scrape the course data for this
            # target.
            else:
                scraper.scrape(args)

        except NotImplementedError as e:
            log.warn("Target %s has not been defined. Skipping." % target )

        log.info("Disengaging scraper engine.")


def clean(args, string):
    """
    Perform a standard cleaning procedure on a course description. Includes
    stop word removal, non-English character removal, digit removal, etc.
    """

    import logging, re
    log = logging.getLogger("root")

    from porterstemmer import Stemmer
    stem_word = Stemmer()

    # Remove non alphanumerics.
    string = string.lower()
    string = ''.join(c if c.isalnum() else ' ' for c in string)
    nonalnum = re.compile("\\\\n|\\\\r|\\\\xa0|\d|\W|\s")
    string = re.sub(nonalnum, ' ', string)

    # Perform stopword removal using a cached stopword object.
    # Additionally, perform stemming on each word.
    from trajectory import config as TRJ
    string = ' '.join(set([stem_word(word) for word in string.split()
                            if word not in TRJ.STOP_WORDS]))

    # Remove singletons or pairs of letters.
    singletons = re.compile("(?<!\w)\w{1,2}(\s|$)")
    string = re.sub(singletons, "", string)

    # Remove strings of whitespace characters.
    long_whitespace = re.compile("\s+")
    string = re.sub(long_whitespace, ' ', string)

    # Remove strings with fewer than 5 words, since they were likely
    # cleaned incorrectly.
    if len(string.split(" ")) < 5:
        log.warn("String too short, marked for deletion.")
        string = None

    # Return cleaned string.
    return string


def export(args):
    """
    Read all data from the database and store it to disk for analysis.
    """

    from trajectory.models import Course, Department, University
    import os

    import logging, re
    log = logging.getLogger("root")
    log.info("Begin data export.")

    # Create the base output directory in the temporary store for copying
    # over later.
    data = os.path.join(args.tmp, "data")
    os.mkdir(data)
    log.debug("Creating folder %s." % data)

    # Get access to the data.
    universities = args.session.query(University).all()

    # Dump data in folders broken down by university.
    for university in universities:

        # Create folder to store univerity data.
        path = os.path.join(data, university.abbreviation)
        os.mkdir(path)
        log.debug("Creating folder %s." % path)

        # Retrieve and flatten course list.
        departments = university.departments
        courses = [department.courses for department in departments]
        courses = [course for department in courses for course in department]

        label = lambda course: "%s_%s.txt" % \
                (course.department.abbreviation, course.number)

        # Write course descriptions to files.
        for course in courses:
            course_path = os.path.join(path, label(course))
            with open(course_path, "w") as course_file:
                course_file.write(course.description)

    log.info("Data export complete.")
