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

    log.info("Scraping targets: %s" % args.target)

    for target in args.target:
        log.info("Targeting: %s" % target)
