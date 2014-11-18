"""
trajectory/scrape/__init__.py
Author: Jean Michel Rouly

Scrape data to generate a syllabus data set.
"""


__all__ = ["engines"]


def scrape(args):
    """
    Routes scraping to the appropriate scraper module.
    """


    import logging
    import os
    from importlib import import_module


    log = logging.getLogger("root")
    log.info("Scraping targets: %s" % args.targets)




    # Create data directory, if it doesn't already exist.
    # Also make sure that the raw/clean subdirectories exist within it.
    if not os.path.exists( args.data_dir ):
        log.info("\"%s\" does not exist. Creating..." % args.data_dir)
        os.makedirs( args.data_dir )

    # Ensure raw path exists.
    raw_path = os.path.join( args.data_dir, "raw" )
    if not os.path.exists( raw_path ):
        log.info("\"%s\" does not exist. Creating..." % raw_path )
        os.makedirs( raw_path )

    # Ensure clean path exists.
    clean_path = os.path.join( args.data_dir, "clean" )
    if not os.path.exists( clean_path ):
        log.info("\"%s\" does not exist. Creating..." % clean_path )
        os.makedirs( clean_path )




    # Loop over the requested targets and call their scrape function.
    for target in args.targets:
        log.info("Targeting: %s" % target)

        # Prepend the target name with a dot for importing.
        target_mod = ".%s" % target
        scraper = import_module( target_mod, "trajectory.scrape.engines" )

        # If downloading is flagged, run it.
        if args.download:
            try:
                scraper.scrape( args )
            except NotImplementedError as e:
                log.warn( "%s has not been defined. Skipping." % target )

        # If cleaning is flagged, run it.
        if args.clean:
            try:
                scraper.clean( args )
            except NotImplementedError as e:
                log.warn( "%s has not been defined. Skipping." % target )

