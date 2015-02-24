# Trajectory

[![Join the chat at https://gitter.im/jrouly/trajectory](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jrouly/trajectory?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Trajectory is a working title for my CS 390 undergraduate research project.
I am taking university syllabus data and applying LDA topic modeling.

## Requirements

The basic requirements are Java JDK 7 or higher, Python 3.0 or higher.
Optionally, the system dependencies `catdoc` and `pdftotext` are
recommended for converting DOC and PDF syllabus datasets to standard
textual formats.


## Setup

Note that this project contains an unholy combination of Bash scripts,
Python tools, and Java code. Proceed with setup carefully.

Begin by exporting the `$TRJ_HOME` path variable.

    $ export TRJ_HOME=$(pwd)

Running the setup script will create and activate a virtual environment and
install Python requirements.

    $ bin/setup

You will also need to build any compiled code.

    $ bin/build

## Use

To scrape and process downloaded syllabus data, use the `trj-scrape`
script.

    $ bin/trj-scrape [-h] [--version] [--debug] {scrape,clean} {targets}

### To download syllabi from a prebuilt target

#### Scrape: Download

    $ bin/trj-scrape scrape [target] --download

#### Scrape: Clean

Cleaning processes the raw syllabus data, removing meta data, and resulting
in single-line bags of words.

    $ bin/trj-scrape scrape [target] --clean

#### Data: Clean

Cleaning the data directory refers to deleting the downloaded and processed
syllabus data.

    $ bin/trj-scrape clean {data,logs,all}

### LDA Topic Modeling

To run LDA topic modeling, use the `trj-learn` script.

    $ bin/trj-learn -data <path> [-debug] [-iterations <num>] [-threads <num>]

