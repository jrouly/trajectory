Author: Jean Michel Rouly
Date:   2014-10-05

# Setup

Note that this project contains an unholy combination of Bash scripts,
Python tools, and Java code. Proceed with setup carefully.

Begin by exporting the `$TRJ_HOME` path variable.

    $ export TRJ_HOME=$(pwd)

Running the setup script will create and activate a virtual environment and
install Python requirements.

    $ bin/setup

You will also need to build any compiled code.

    $ bin/build

# Use

To scrape and process downloaded syllabus data, use the `trj-scrape`
script.

    $ bin/trj-scrape [-h] [--version] [--debug] {scrape,clean} {targets}

To run LDA topic modelling, use the `trj-learn` script.

    $ bin/trj-learn -data <path> [-debug] [-iterations <num>] [-threads <num>]

