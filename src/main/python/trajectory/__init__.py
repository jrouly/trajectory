"""
trajectory/__init__.py
Author: Jean Michel Rouly

Define the trajectory package.
"""


from trajectory import engines
from trajectory import log


__all__ = ["log", "engines"]



def scrape(args):
    """
    Routes scraping to the appropriate scraper module.
    """


    from trajectory import database
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
            database.register_target(args, scraper.META)
        except AttributeError as e:
            log.warn("Target %s metadata not defined." % target)
            log.warn("Terminating engine.")
            log.debug(e)
            return


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
