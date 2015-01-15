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
            pass
            #database.register( args, scraper.META )
        except AttributeError:
            log.warn( "Target %s metadata malformed." % target )


        if args.download:
            try:
                scraper.scrape( args, target_raw_path )
            except NotImplementedError as e:
                log.warn( "Target %s has not been defined. Skipping." %
                        target )


        if args.digest:
            try:
                scraper.clean( args, target_raw_path, target_clean_path )
            except NotImplementedError as e:
                log.warn( "Target %s has not been defined. Skipping." %
                        target )


        if not (args.digest or args.download):
            log.warn("No action performed.")


        log.info("Disengaging scraper engine.")
