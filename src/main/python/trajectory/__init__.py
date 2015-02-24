"""
trajectory/__init__.py
Author: Jean Michel Rouly

Define the trajectory package.
"""


from trajectory import log, engines


__all__ = ["log", "engines"]


def scrape(args):
    """
    Routes scraping to the appropriate scraper module.
    """

    from trajectory.models import University, Department

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
        log.info("Registering target with database.")
        try:
            metadata = scraper.META
            university = metadata.get("school")

            # Verify that this university hasn't already been registered.
            if(args.session.query(University)\
                   .filter(University.name==university.get("name"))\
                   .count() == 0):

                university = University(
                        name=university.get("name"),
                        abbreviation=university.get("abbreviation"),
                        url=university.get("url"))
                departments = metadata.get("departments")
                for department in departments:
                    university.departments.append(Department(
                            name=department.get("name"),
                            abbreviation=department.get("abbreviation"),
                            url=department.get("url")))

                # Add these objects to the session.
                args.session.add(university)

            else:
                log.info("Target metadata already loaded in database.")

        except AttributeError as e:
            log.warn("Target %s metadata not defined." % target)
            log.warn("Terminating engine.")
            log.debug(e)
            continue

        # Download data into the temporary directory under "data".
        if (not args.debug) or (args.debug and args.download):
            try:
                scraper.scrape(args)
            except NotImplementedError as e:
                log.warn( "Target %s has not been defined. Skipping." %
                        target )

        else:
            log.warn("No action performed.")

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

