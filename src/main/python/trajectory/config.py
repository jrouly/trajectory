"""
trajectory/config.py
Author: Jean Michel Rouly

Define globally accessible environment.
"""


# Program identification and versioning.
PROGRAM_NAME = "Trajectory"
PROGRAM_DESC = "This Python application is used to acquire (scrape, clean) a dataset."
PROGRAM_VERSION = PROGRAM_NAME + " 0.1"

# Program home directory.
import sys, os, json
if os.environ.get("TRJ_HOME") is None:
    print("Environment variable TRJ_HOME not set. Exiting.")
    sys.exit( 1 )
else:
    HOME = os.environ.get("TRJ_HOME")

# Database location.
DATABASE_URI = "sqlite:///%s" % os.path.join(HOME, "data.db")
#DATABASE_URI = "postgresql://user@localhost/mydatabase"
#DATABASE_URI = "mysql://user@localhost/mydatabase"

# Resource locations.
__RESOURCES = os.path.join(HOME, "src", "main", "resources")

# ACM Data Files
ACM_EXEMPLARS = os.path.join(__RESOURCES, "acm", "exemplar-descriptions.txt")
ACM_KA = os.path.join(__RESOURCES, "acm", "knowledge-areas.txt")
KA_TRUTH = json.load(open(os.path.join(__RESOURCES, "acm", "ground-truth.json")))

# Stop words cache.
__STOP_WORDS_FILE = os.path.join(HOME, __RESOURCES, "stoplists", "en.txt")
STOP_WORDS = set(open(__STOP_WORDS_FILE, "r").read().splitlines())

# Engine metadata cache.
ENGINE_METADATA = os.path.join(__RESOURCES, "engine_metadata")

# Minimum topic weight to measure.
TOPIC_MIN_WEIGHT = 0.15

# Directory where templates are stored for the visualization module.
TEMPLATES = os.path.join(__RESOURCES, "web", "templates")
STATIC_FILES = os.path.join(__RESOURCES, "web", "static")
