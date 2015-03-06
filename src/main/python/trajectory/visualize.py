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
            'ulist': os.path.join(args.vis_directory, "university_list.html"),
    }

    # Compute and create university directories.
    universities = args.session.query(University).all()
    for university in universities:
        uni_path = os.path.join(
                args.vis_directory,
                "universities",
                university.abbreviation)
        paths[university.abbreviation] = uni_path
        os.makedirs(uni_path)

    # Generate static about page.
    with open(paths['about'], "w") as fp:
        template = env.get_template("about.html")
        fp.write(template.render())

    # Generate dashboard page.
    with open(paths['index'], "w") as fp:
        template = env.get_template("index.html")

        # number of courses offered by a university
        num_courses_by_uni = lambda uni: \
            sum([len(department.courses) for department in uni.departments])
        uni_link = lambda uni: \
            "university_list.html#%s" % uni.abbreviation

        # { GMU : (page, totalNumCourses), UMD : (page, totalNumCourses) ... }
        uni_num_courses = {university : (uni_link(university),
                                        num_courses_by_uni(university))
                            for university in universities}

        fp.write(template.render(universities=uni_num_courses))

    # Generate university list page.
    with open(paths['ulist'], "w") as fp:

        # Compute university information tuples.
        # [{
        #   'university': <University Object>,
        #   'index-page': university.html,
        #   'departments': [(<Department>, page), (<Department>, page)]
        # }]
        university_list = []
        for university in universities:
            uni_dir = os.path.join("universities", university.abbreviation)
            uni_index = os.path.join(uni_dir, "index.html")
            departments = [
                (department, os.path.join(uni_dir, "%s.html" \
                        % department.abbreviation))
                for department in university.departments]

            university_list.append({
                "university": university,
                "index-page": uni_index,
                "departments": departments
            })

        template = env.get_template("university_list.html")
        fp.write(template.render(university_list=university_list))

    # Generate departmental pages.
    for university in universities:
        uni_dir = paths[university.abbreviation]
        for department in university.departments:
            department_path = os.path.join(uni_dir, "%s.html" % \
                    department.abbreviation)
            with open(department_path, "w") as fp:
                template = env.get_template("department.html")
                fp.write(template.render(department=department))



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
