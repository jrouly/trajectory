"""
trj.py
Author: Jean Michel Rouly

This is the main executable file. Use it to call subcommands in the
application structure.
"""


from argparse import ArgumentParser
import trajectory.log
import traceback
import sys
import os

from trajectory import engines
from trajectory import config as TRJ
from trajectory.core import scrape, export, import_results, visualize
from trajectory.models.meta import Engine, Session

def main():
    """
    Handle basic command line argument parsing & configure logging. Route
    logic depending on what the user wants to do.
    """

    # Create top-level command line argument parser.
    parser = ArgumentParser(description=TRJ.PROGRAM_DESC, prog=TRJ.PROGRAM_NAME)
    parser.add_argument("--version", action="version", version=TRJ.PROGRAM_VERSION)
    parser.add_argument("--debug", action="store_true")
    subparsers = parser.add_subparsers(dest="command",
        help="Either download new data or export existing data to disk.")

    # Create arguments for scraping.
    download_parser = subparsers.add_parser("download",
            help="Download data from the Web.")
    download_parser.add_argument("targets", choices=engines.list(),
            nargs="+",
            help="Scraping targets, select one or more.")

    # Create arguments for exporting.
    export_parser = subparsers.add_parser("export",
            help="Export data to disk for analysis.")
    export_parser.add_argument("--data-directory",
            required=True,
            help="The data directory to store in.",
            action="store")

    # Create arguments for importing topics.
    import_parser = subparsers.add_parser("import-results",
            help="Import learned topics to the database.")
    import_parser.add_argument("--topic-file",
            required=True,
            help="The stored topic key file from the learn module.",
            action="store")
    import_parser.add_argument("--course-file",
            required=True,
            help="The stored document key file from the learn module.",
            action="store")

    # Create arguments for visualization module.
    vis_parser = subparsers.add_parser("visualize",
            help="Generate visualization tool.")
    vis_parser.add_argument("--vis-directory",
            required=True,
            help="Where to store the generated tool.",
            action="store")
    vis_parser.add_argument("--serve",
            required=False,
            help="Serve the tool once generated.",
            action="store_true")
    vis_parser.add_argument("--port",
            required=False,
            help="Port to serve on.",
            action="store")

    # Parse command line arguments.
    args = parser.parse_args(sys.argv[1:])

    # Start up the program.
    log = trajectory.log.global_logger("root", debug=args.debug)
    log.info("Beginning trj-scrape.")
    log.info("Initializing database connection.")
    args.session = Session()

    # Wrap main control flow in a try/catch for safety.
    try:

        # Hand off control flow to export module.
        if args.command == "export":
            export(args)

        # Hand off control flow to scraper module.
        elif args.command == "download":
            scrape(args)

        # Hand off control to the import module.
        elif args.command == "import-results":
            import_results(args)

        # Hand off control to the visualize module.
        elif args.command == "visualize":
            visualize(args)

        # Otherwise no command was selected
        else:
            log.info("No command specified.")

        # Store any modifications to the database.
        args.session.commit()

    # Handle any unknown errors gracefully.
    except Exception as error:

        log.warn("Unknown error encountered.")
        log.warn(error)
        if args.debug:
            traceback.print_exc()

    # Shut down safely.
    finally:

        # Exit the program.
        log.info("Exiting.")
        args.session.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
