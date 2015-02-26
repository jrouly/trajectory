# Trajectory

[![Join the chat at https://gitter.im/jrouly/trajectory](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jrouly/trajectory?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Trajectory is a working title for my CS 390 undergraduate research project. I am taking university course description data and applying LDA topic modeling.

## Requirements

The basic requirements are Java JDK 7 or higher, Python 3.0 or higher. Support for the database layer requires system copies of MySQL, PostGres, SQLite, or similar software.


## Setup

Note that this project contains an unholy combination of Bash scripts, Python tools, and Java code. Proceed with setup carefully.

Begin by exporting the `$TRJ_HOME` path variable.

    $ git clone http://github.com/jrouly/trajectory
    $ cd trajectory
    $ export TRJ_HOME=$(pwd)

You will also need to build any compiled code.

    $ bin/util/build

If at any time you wish to clear the compiled code, execute the included clean script.

    $ bin/util/clean

To specify or change the database URI and scheme, modify the `config.py` file. Specifically, look for `DATABASE_URI`. It defaults to a SQLite file named `data.db`.

## Use

To scrape and process downloaded syllabus data, use the `bin/scrape` script.

    $ bin/scrape [-h] [--version] [--debug]
                  {download,export,import-topics} ...

To execute the learning module, use the `bin/learn` script.

    $ bin/learn -debug -in <path> [-iterations <n>]
                  [-out <path>] [-threads <n>] [-topics <n>]

### Download syllabi from a prebuilt target

    $ bin/scrape download [-h] {targets}

### Export downloaded data to disk

    $ bin/scrape export [-h] --data-directory <directory>

This exports data in a format that can be read in by the `Learn` module.

### Run Topic Modeling

    $ bin/learn -debug -in <path> [-iterations <n>]
                  [-out <path>] [-threads <n>] [-topics <n>]

If the `-out <path>` is not specified, data will be printed to standard output. Otherwise, it will be printed to timestamped CSV files that can be read into the `Visualize` module.
