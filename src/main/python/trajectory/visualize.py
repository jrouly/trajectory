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

    from sqlalchemy.sql.expression import func
    from jinja2 import Environment, FileSystemLoader
    import shutil, os, logging

    # Initialize logger.
    log = logging.getLogger("root")
    log.info("Begin visualization generation.")

    # Load static files.
    shutil.copytree(
            TRJ.STATIC_FILES,
            os.path.join(args.vis_directory, "static"))

    # Compute initial output file paths.
    paths = {
            'index': os.path.join(args.vis_directory, "index.html"),
            'about': os.path.join(args.vis_directory, "about.html"),
            'ulist': os.path.join(args.vis_directory, "universities.html"),
            'topics': os.path.join(args.vis_directory, "topics.html"),
    }

    # Compute and create university & department directories.
    universities = args.session.query(University).all()
    for university in universities:
        university_dir = os.path.join(
                args.vis_directory,
                "universities",
                university.abbreviation.lower())
        os.makedirs(university_dir)
        paths[university] = os.path.join(
                university_dir,
                "index.html")
        for department in university.departments:
            paths[department] = os.path.join(
                    university_dir,
                    "%s.html" % department.abbreviation.lower())

    # Get the number of courses per university and per department.
    university_course_count = lambda university: \
        sum([len(department.courses) for department in university.departments])
    department_course_count = lambda department: len(department.courses)

    # Standardize link format.
    university_link = lambda university: \
        "/universities/%s/index.html" % university.abbreviation.lower()
    department_link = lambda department: \
        "/universities/%s/%s.html" % (
            department.university.abbreviation.lower(),
            department.abbreviation.lower()
        )
    course_link = lambda course: \
        "%s#%d" % (
            department_link(course.department),
            course.id
        )
    topic_link = lambda topic: \
        "/topics.html#%d" % topic.id

    # Start up Jinja2.
    env = Environment(loader=FileSystemLoader(TRJ.TEMPLATES))
    env.filters['university_course_count'] = university_course_count
    env.filters['department_course_count'] = department_course_count
    env.filters['university_link'] = university_link
    env.filters['department_link'] = department_link
    env.filters['course_link'] = course_link
    env.filters['topic_link'] = topic_link

    # Generate static about page.
    with open(paths['about'], "w") as fp:
        template = env.get_template("about.html")
        fp.write(template.render())

    # Generate dashboard page.
    with open(paths['index'], "w") as fp:
        template = env.get_template("index.html")
        fp.write(template.render(universities=universities))

    # Generate university list page.
    with open(paths['ulist'], "w") as fp:
        template = env.get_template("universities.html")
        fp.write(template.render(universities=universities))

    # Generate university and departmental pages.
    for university in universities:
        with open(paths[university], "w") as fp:
            template = env.get_template("university.html")
            fp.write(template.render(university=university))

        for department in university.departments:
            with open(paths[department], "w") as fp:
                template = env.get_template("department.html")
                fp.write(template.render(department=department))

    # Generate list of topics sorted by number of documents.
    topics = args.session.query(Topic) \
            .join(CourseTopicAssociation) \
            .group_by(Topic.id) \
            .order_by(func.count().desc()) \
            .all()
    with open(paths['topics'], "w") as fp:
        template = env.get_template("topics.html")
        fp.write(template.render(topics=topics))



def serve(args):
    """
    Serve a simple HTTP server from the visualization directory.
    """

    import http.server
    import socketserver
    import logging, os
    log = logging.getLogger("root")
    os.chdir(args.vis_directory)

    PORT = int(args.port) if args.port else 8000
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    log.info("Serving at port %d" % PORT)
    httpd.serve_forever()
