"""
trajectory.py
Author: Jean Michel Rouly

Important things should go here.
"""


from argparse import ArgumentParser

import logging
import os
import sys


def main():
    """
    Handle basic command line argument parsing & configure logging. Route
    logic depending on what the user wants to do.
    """

    # Constant values.
    PROG_NAME = "Trajectory"
    PROG_DESC = "Trajectory is ... desc here ... "
    PROG_VERSION = PROG_NAME + " 0.0"

    SCRAPE_TARGETS = ["gmu.cs"]

    # Create top-level command line argument parser.
    parser = ArgumentParser(description=PROG_DESC, prog=PROG_NAME)
    parser.add_argument("--version", action="version", version=PROG_VERSION)
    parser.add_argument("--debug", action="store_true",
            help="Show debugging output")
    subparsers = parser.add_subparsers(help="Indicate which subcommand to run.")

    # Create parser for "scrape" command.
    parser_scrape = subparsers.add_parser("scrape", help="Scrape syllabi.")
    parser_scrape.add_argument("target", choices=SCRAPE_TARGETS,
            help="target website to scrape.")

    parser_clean = subparsers.add_parser("clean", help="Clean data folders.")

    # Parse command line arguments.
    args = parser.parse_args(sys.argv[1:])


    # Logging handlers: stream output by default.
    handlers = [ logging.StreamHandler( sys.stdout ) ]

    # Configure logging object.
    logging.basicConfig(handlers=handlers,
                        level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(levelname)8s: %(message)s")

    # Start up program.
    logging.info("Beginning.")


if __name__ == '__main__':
    main()
