from flask import Flask, render_template, url_for, abort
from flask import make_response, request
from jinja2 import FileSystemLoader
from sqlalchemy.sql.expression import func

from trajectory import config as TRJ
from trajectory.models import University, Department, Course, ResultSet
from trajectory.models import Topic, CourseTopicAssociation
from trajectory.models.meta import Session


#####################
# Application Setup #
#####################

app = Flask(__name__)
app.config.from_object(dict(
    DEBUG = True,
    THREADS_PER_PAGE = 8,
))
app.jinja_loader = FileSystemLoader(TRJ.TEMPLATES)
app.db = Session()


###################
# View Definition #
###################

# Manage error handling.
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Define routing for dashboard page.
@app.route('/')
def dashboard():
    universities = app.db.query(University).all()
    result_sets = app.db.query(ResultSet).all()
    response = make_response(render_template(
            "index.html",
            universities=universities,
            result_sets=result_sets))

    # Set the 'active' result set as the first available one.
    if len(result_sets) > 0:
        response.set_cookie('result_set', str(result_sets[0].id))

    return response

# Define routing for university list.
@app.route('/universities/')
def university_list():
    universities = app.db.query(University).all()
    return render_template("universities.html", universities=universities)

# Define routing for university index pages.
@app.route('/universities/<string:u>/')
def university(u=None):
    university = app.db.query(University) \
            .filter(University.abbreviation==u).first()
    if university is None:
        abort(404) # university not found
    return render_template("university.html", university=university)

# Define routing for departmental pages.
@app.route('/universities/<string:u>/<string:d>/')
def department(u=None, d=None):
    department = app.db.query(Department).join(University) \
            .filter(University.abbreviation==u) \
            .filter(Department.abbreviation==d).first()
    if department is None:
        abort(404) # department not found
    return render_template("department.html", department=department)

# Define routing for topic list.
@app.route('/topics/')
def topics():
    topics = app.db.query(Topic) \
            .join(CourseTopicAssociation) \
            .group_by(Topic.id) \
            .order_by(func.count().desc()) \
            .all()
    return render_template("topics.html", topics=topics)

# Define routing for about page.
@app.route('/about/')
def about():
    return render_template("about.html")


######################
# Filter Definitions #
######################

@app.template_filter('course_count')
def course_count(data):
    if type(data) == University:
        return sum([len(department.courses)
            for department in data.departments])
    elif type(data) == Department:
        return len(data.courses)
    else:
        return 0
