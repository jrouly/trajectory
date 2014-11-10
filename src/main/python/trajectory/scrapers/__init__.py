"""
trajectory/scrapers/__init__.py
Author: Jean Michel Rouly

Define a set of backend engines for obtaining syllabus data.
"""


def scrapers():
    from pkgutil import iter_modules
    from trajectory import scrapers
    modules = iter_modules( trajectory.scrapers.__path__ )
    return [ mod[1] for mod in modules ]


__all__ = scrapers()
