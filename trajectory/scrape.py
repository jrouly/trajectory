"""
trajectory/scrape.py
Author: Jean Michel Rouly

Route the scraping of syllabi data.
"""


import pkgutil
import logging
log = logging.getLogger("root")


# Constant values.
# TODO: These should be read from a configuration at some point.
SCRAPE_TARGETS = ["gmu.cs"]


def scrape(args):
    """
    Routes scraping to the appropriate scraper module.
    """

    log.info("Scraping targets: %s" % args.targets)

    for target in args.targets:
        log.info("Targeting: %s" % target)
        packagename = "trajectory.scrapers.%s" % target
        scraper = __import__( packagename )
