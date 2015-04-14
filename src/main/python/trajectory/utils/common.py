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
