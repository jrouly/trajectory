"""
trajectory/utils/common.py
Author: Jean Michel Rouly

Define a collection of useful utility functions.
"""


def row2dict(row):
    """
    Convert a SQLAlchemy row to a dictionary.
    """
    return {
        col.name: getattr(row, col.name)
        for col in row.__table__.columns
    }


def jaccard(a, b):
    """
    Calculate the jaccard coefficient of two lists.
    """

    n = len(a.intersection(b))
    d = float(len(a) + len(b) - n)
    if d == 0:
        return 1
    return n / d


