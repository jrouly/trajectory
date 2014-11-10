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
    from importlib import import_module

    log = logging.getLogger("root")
    log.info("Scraping targets: %s" % args.targets)


    # Loop over the requested targets and call their scrape function.
    for target in args.targets:
        log.info("Targeting: %s" % target)

        target = ".%s" % target # prepend with a dot
        scraper = import_module( target, "trajectory.scrape.engines" )

        try:
            scraper.scrape( args )
            if not args.download_only:
                scraper.clean( args )
        except NotImplementedError as e:
            log.debug( str(e) )
