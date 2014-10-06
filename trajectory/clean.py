"""
trajectory/clean.py
Author: Jean Michel Rouly

Clean up all generated directories.
"""


import os
import shutil
import logging
log = logging.getLogger("root")


# Constant values.
# TODO: These should be read from a configuration at some point.
CLEAN_TARGETS = ["all", "data", "logs"]


def clean(args):
    """
    Cleans all generated content: logs, data, etc.
    """

    log.info("Cleaning: %s" % args.target)

    # Delete log directory.
    if "logs" in args.target or "all" in args.target:
        if os.path.exists( args.logging_dir ):
            log.info("Found log directory \"%s\". Removing...." % args.logging_dir)
            shutil.rmtree( args.logging_dir )
        else:
            log.info("No logs to remove.")

    # Delete data directory.
    if "data" in args.target or "all" in args.target:
        if os.path.exists( args.data_dir ):
            log.info("Found data directory \"%s\". Removing...." % args.data_dir)
            shutil.rmtree( args.data_dir )
        else:
            log.info("No data to remove.")
