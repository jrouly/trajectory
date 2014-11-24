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


    import logging
    import os
    from importlib import import_module


    log = logging.getLogger("root")
    log.info("Selected scraping targets: %s." % args.targets)


    # Create data directory, if it doesn't already exist.
    # Also make sure that the raw/clean subdirectories exist within it.
    if not os.path.exists( args.data_dir ):
        log.info("Data directory \"%s\" does not exist. Creating." % args.data_dir)
        os.makedirs( args.data_dir )

    # Ensure raw path exists.
    raw_path = os.path.join( args.data_dir, "raw" )
    if not os.path.exists( raw_path ):
        log.info("Raw data directory \"%s\" does not exist. Creating." % raw_path )
        os.makedirs( raw_path )

    # Ensure clean path exists.
    clean_path = os.path.join( args.data_dir, "clean" )
    if not os.path.exists( clean_path ):
        log.info("Clean data directory \"%s\" does not exist. Creating." % clean_path )
        os.makedirs( clean_path )


    # Loop over the requested targets and call their scrape function.
    for target in args.targets:


        log.info("Engaging scraper engine: %s" % target)


        # Prepend the target name with a dot for importing.
        target_module = ".%s" % target
        scraper = import_module( target_module, "trajectory.engines" )


        # Define the raw and clean paths specific to this target engine.
        target_raw_path = os.path.join( raw_path, target )
        target_clean_path = os.path.join( clean_path, target )


        # If downloading is flagged, run it.
        if args.download:
            try:


                # If the target raw path does not exist, create it.
                # If it does exist, then warn the user.
                if not os.path.exists( target_raw_path ):
                    log.info("\"%s\" does not exist. Creating..." %
                            target_raw_path )
                    os.makedirs( target_raw_path )
                else:
                    log.info("\"%s\" already exists." % target_raw_path )


                # Run the engine's scraper method.
                scraper.scrape( args, target_raw_path )


            except NotImplementedError as e:


                # If the scraper function isn't defined, throw up
                # gracefully and continue.
                log.warn( "Target %s has not been defined. Skipping." %
                        target )


        # If cleaning is flagged, run it.
        if args.digest:
            try:


                # If the target clean path does not exist, create it.
                # If it does exist, then warn the user.
                if not os.path.exists( target_clean_path ):
                    log.info("\"%s\" does not exist. Creating..." %
                            target_clean_path )
                    os.makedirs( target_clean_path )
                else:
                    log.info("\"%s\" already exists." % target_clean_path )


                # Run the engine's clean method.
                scraper.clean( args, target_raw_path, target_clean_path )


            except NotImplementedError as e:


                # If the clean function isn't defined, throw up gracefully
                # and continue.
                log.warn( "Target %s has not been defined. Skipping." %
                        target )


        # If neither clean nor download were flagged, notify the user.
        if not args.digest and not args.download:
            log.warn("Heads up, no action performed.")


        log.info("Disengaging scraper engine.")
