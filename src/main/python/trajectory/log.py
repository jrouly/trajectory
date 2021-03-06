"""
trajectory/log.py
Author: Jean Michel Rouly

Configure a global logging system.
"""


import logging


def global_logger(name, debug=False):
    """
    Generate a global logger object.
    """

    #formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.addHandler(handler)

    return logger
