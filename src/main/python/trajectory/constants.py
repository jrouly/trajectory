# Program identification and versioning.
PROGRAM_NAME = "Trajectory"
PROGRAM_DESC = "This Python application is used to acquire (scrape, clean) a dataset."
PROGRAM_VERSION = PROGRAM_NAME + " 0.1"

# Program home directory.
import sys, os
if os.environ.get("TRJ_HOME") is None:
    print("TRJ_HOME not found. Exiting.")
    sys.exit( 1 )
else:
    HOME = os.environ.get("TRJ_HOME")

# Database location.
DATABASE_URI = "sqlite:///data.db"
