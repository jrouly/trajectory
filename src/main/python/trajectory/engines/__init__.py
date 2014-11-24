"""
trajectory/scrape/engines/__init__.py
Author: Jean Michel Rouly

Backends for the scraper engine.
"""


def list():
    """
    List the available scraper engines.
    """

    from pkgutil import iter_modules
    modules = iter_modules( __path__ )
    return [ mod[1] for mod in modules ]


__all__ = list()
