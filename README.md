Author: Jean Michel Rouly
Date:   2014-10-05

# Setup

### Install Python requirements

    $ virtualenv env
    $ pip install -r requirements.txt


### Compile Java utilities

    $ mvn compile

Note: make sure to define the M2_REPO classpath variable to point to your
Maven repository.

# Use

    $ python usage: Trajectory [-h] [--version] [--debug] {scrape,clean} ...

