"""
trajectory/clean.py
Author: Jean Michel Rouly

Clean up all generated directories.
"""


import os
import shutil
import logging
log = logging.getLogger("root")


# Available targets to clean.
TARGETS = ["all", "data", "logs"]


def clean(args):
    """
    Cleans all generated content: logs, data, etc.
    """

    log.info("Cleaning: %s" % args.targets)

    # Delete logs.
    if "logs" in args.targets or "all" in args.targets:
        if os.path.exists( args.logging_dir ):

            log.info("Found log directory \"%s\". Removing contents." % args.logging_dir)

            for the_file in os.listdir( args.logging_dir ):
                file_path = os.path.join( args.logging_dir, the_file )
                try:
                    if os.path.isfile( file_path ):
                        os.remove( file_path )
                    else:
                        shutil.rmtree( file_path )
                except Exception as e:
                    print( e )

        else:
            log.info("No logs to remove.")

    # Delete data directory.
    if "data" in args.targets or "all" in args.targets:
        if os.path.exists( args.data_dir ):

            log.info("Found data directory \"%s\". Removing contents." % args.data_dir)

            for the_file in os.listdir( args.data_dir ):
                file_path = os.path.join( args.data_dir, the_file )
                try:
                    if os.path.isfile( file_path ):
                        os.remove( file_path )
                    else:
                        shutil.rmtree( file_path )
                except Exception as e:
                    print( e )

        else:
            log.info("No data to remove.")
