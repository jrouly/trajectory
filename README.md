# Trajectory

[![Join the chat at https://gitter.im/jrouly/trajectory](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jrouly/trajectory?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Trajectory is a software platform for automatically extracting topics from university course descriptions. It includes modules for data ingestion, learning, and visualization.

## Requirements

The basic requirements are Java JDK 7 or higher, Python 3.0 or higher, `virtualenv`, and `maven`. Support for the database layer requires system copies of MySQL, PostGres, SQLite, or similar software. Support for the visualization layer requires a proxy web server (eg. Apache, Nginx).


## Setup

Note that this project contains an unholy combination of Bash scripts, Python tools, and Java code. Proceed with setup carefully.

Begin by exporting the `$TRJ_HOME` path variable.

    $ git clone http://github.com/jrouly/trajectory
    $ cd trajectory
    $ export TRJ_HOME=$(pwd)

Install Python dependencies by calling the `bin/util/pysetup` script. Java code will be compiled on demand.

To specify or change the database URI and scheme, modify the `config.py` file. Specifically, look for `DATABASE_URI`. It defaults to a SQLite file named `data.db`.

### Visualization server

#### Sample nginx configuration

    server {
        listen 80;
        location ^~ /static/  {
            root /TRJ_HOME/src/main/resources/web/static;
        }

        location / {
            proxy_pass         http://localhost;
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    }

## Use

### Download data from a prebuilt target

    $ bin/scrape download [-h] {targets}

### Export downloaded data to disk

    $ bin/scrape export [-h] [--data-directory <directory>]
                  [--departments <departments>] [--cs]

This exports data in a format that can be read in by the `Learn` module. The data directory will default to `data/`. You can selectively filter subjects exported using the `--departments` flag.

### Run Topic Modeling

    $ bin/learn -in <path> -out <path> [-iterations <n>] [-debug]
                  [-threads <n>] [-topics <n>] [-words <n>]
                  [-alpha <alpha>] [-beta <beta>]

The `-in` parameter must be an export location from the `Scrape` module. Results will be stored within a timestamped subdirectory of the `-out` directory. All other parameters are optional.

### Import topic modeling to database

    $ bin/scrape import-results [-h] --topic-file <file> --course-file <file>
                  [--alpha <alpha>] [--beta <beta>] [--iterations <iterations>]

Read the results of the `Learn` module (inferred topics) back into the database and pair with existing course data. Multiple imports will simply add `ResultSet`s to the existing database.

### Run visualizations server

    $ bin/web

Activate the visualization server. See `gunicorn.py` for configuration settings. Notice that the PID and log files are stored in the `TRJ_HOME`.

# ToDo

1. Create common engine frameworks for catalog installs to be more DRY.
2. Refactor configuration objects as a module.
