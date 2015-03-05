"""
trajectory/visualize.py
Author: Jean Michel Rouly

Define functionality to generate and display collected data.
"""


def generate_html(args):
    """
    Generate static HTML pages based on information in the database.
    """

    from trajectory.models import Course, Topic, CourseTopicAssociation
    from trajectory.models import University, Department
    from trajectory import config as TRJ

    from jinja2 import Environment, FileSystemLoader
    import shutil, os, logging

    # Initialize logger.
    log = logging.getLogger("root")
    log.info("Begin visualization generation.")

    # Start up Jinja2.
    env = Environment(loader=FileSystemLoader(TRJ.TEMPLATES))

    # Load static files.
    shutil.copytree(
            TRJ.STATIC_FILES,
            os.path.join(args.vis_directory, "static"))

    # Compute initial output file paths.
    paths = {
            'index': os.path.join(args.vis_directory, "index.html"),
            'about': os.path.join(args.vis_directory, "about.html"),
    }

    # Generate static files.
    with open(paths['index'], "w") as fp:
        template = env.get_template("index.html")
        fp.write(template.render())

    with open(paths['about'], "w") as fp:
        template = env.get_template("about.html")
        fp.write(template.render())


def serve(args):
    """
    Serve a simple HTTP server from the visualization directory.
    """

    import http.server
    import socketserver
    import logging, os
    log = logging.getLogger("root")
    os.chdir(args.vis_directory)

    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    log.info("Serving at port %d" % PORT)
    httpd.serve_forever()
