from flask import Flask, g, render_template, url_for, abort
from flask import make_response, request
from jinja2 import FileSystemLoader
from sqlalchemy.sql.expression import func
import itertools
import pickle

from trajectory import config as TRJ
from trajectory.utils.prereqs import get_prereq_graph
from trajectory.utils.common import jaccard
from trajectory.models import University, Department, Course, ResultSet
from trajectory.models import Topic, CourseTopicAssociation
from trajectory.models.meta import session


#####################
# Application Setup #
#####################

app = Flask(__name__)
app.config.from_object(dict(
    DEBUG = True,
    THREADS_PER_PAGE = 8,
))
app.jinja_loader = FileSystemLoader(TRJ.TEMPLATES)
app.db = session


###################
# View Definition #
###################

# Manage error handling.
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Manage error handling.
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Define routing for dashboard page.
@app.route('/')
def dashboard():
    universities = app.db.query(University).all()
    result_sets = app.db.query(ResultSet).all()
    return render_template("index.html",
            universities=universities,
            result_sets=result_sets)

# Define routing for university list.
@app.route('/universities/')
def university_list():
    universities = app.db.query(University).all()
    return render_template("universities.html",
            universities=universities)

# Define routing for university index pages.
@app.route('/universities/<string:u>/')
def university(u=None):
    university = app.db.query(University) \
            .filter(University.abbreviation==u) \
            .first()
    if university is None:
        abort(404) # university not found
    return render_template("university.html",
            university=university)

# Define routing for departmental pages.
@app.route('/universities/<string:u>/<string:d>/')
def department(u=None, d=None):
    department = app.db.query(Department).join(University) \
            .filter(University.abbreviation==u) \
            .filter(Department.abbreviation==d) \
            .first()
    if department is None:
        abort(404) # department not found
    return render_template("department.html",
            department=department)

# Define routing for a course.
@app.route('/universities/<string:u>/<string:d>/id<string:cid>/')
def course(u=None, d=None, cid=None):
    course = app.db.query(Course).join(Department).join(University) \
            .filter(University.abbreviation==u) \
            .filter(Department.abbreviation==d) \
            .filter(Course.id==cid).first()
    if course is None:
        abort(404)
    return render_template("course.html",
            course=course)

# Define routing for topic list.
@app.route('/topics/')
def topics():
    topics = app.db.query(Topic) \
            .join(CourseTopicAssociation) \
            .join(ResultSet) \
            .group_by(Topic.id, ResultSet.id) \
            .order_by(func.count().desc()) \
            .all()
    return render_template("topics.html",
            topics=topics)

# Define routing for about page.
@app.route('/about/')
def about():
    return render_template("about.html")

# Define routing for course prerequisite tree API endpoint.
@app.route('/prereqs/<string:cid>')
def prereq_tree(cid):
    data = get_prereq_graph(cid, layout=True, format="node")
    if data is None:
        abort(404)
    response = make_response(data)
    response.headers["Content-Disposition"] = \
            "attachment; filename=course-%s-prereqs.json" % cid
    return response

# Define routing for department comparison page.
@app.route('/compare/departments/')
@app.route('/compare/departments/<string:daid>/<string:dbid>/')
def compare_departments(daid=1, dbid=1): #TODO: set more reasonable defaults

    # Look up requested departments.
    department_a = session.query(Department).get(daid)
    department_b = session.query(Department).get(dbid)
    if department_a is None or department_b is None or g.result_set_raw is None:
        abort(404)

    # Identify list of topics for each department, calculate Jaccard
    # coefficient.
    department_a_topics = set(itertools.chain.from_iterable(
        [[t.topic for t in c.topics if t.result_set == g.result_set_raw]
            for c in department_a.courses]))
    department_b_topics = set(itertools.chain.from_iterable(
        [[t.topic for t in c.topics if t.result_set == g.result_set_raw]
            for c in department_b.courses]))
    j_index = jaccard(department_a_topics, department_b_topics)

    # Identify the topics unique to each course.
    intersection = department_a_topics.intersection(department_b_topics)
    department_a_topics = department_a_topics - intersection
    department_b_topics = department_b_topics - intersection

    # Global list of departments for switching over.
    departments = session.query(Department).all()

    return render_template("compare_departments.html",
            da=department_a,
            db=department_b,
            da_topics=department_a_topics,
            db_topics=department_b_topics,
            common_topics=intersection,
            departments=departments,
            jaccard=j_index)

################################
# Custom Filters and Functions #
################################

@app.template_filter('course_count')
def course_count(data):
    if type(data) == University:
        return sum([len(department.courses)
            for department in data.departments])
    elif type(data) == Department:
        return len(data.courses)
    else:
        return 0

# Make the deserialize function available to templates.
@app.context_processor
def utility_processor():
    def unpickle(data):
        try:
            import binascii
            unhex = binascii.unhexlify(data)
            return pickle.loads(unhex)
        except TypeError:
            return None
    return dict(unpickle=unpickle)


#####################
# Request Callbacks #
#####################

# Identify the requested result_set from the user. If none is currently
# selected, just default to the first one.
@app.before_request
def get_result_set():

    # Load the requested and known result set ids.
    # Warning: do NOT call loads on the requested data.
    import binascii
    result_set = request.cookies.get('result_set')
    result_sets = app.db.query(ResultSet).all()
    legal_result_sets = [binascii.hexlify(pickle.dumps(rs)).decode('utf-8')
            for rs in result_sets]

    # Check if the requested id is legal. If not, default it.
    if result_set is None or result_set not in legal_result_sets:
        if len(legal_result_sets) > 0:
            result_set = legal_result_sets[0]
        else:
            result_set = None

    # Look up the raw result set for server-side storage.
    if result_set is not None:
        result_set_index = legal_result_sets.index(result_set)
        result_set_raw = result_sets[result_set_index]
    else:
        result_set_raw = None

    # Set the global current- and legal- resultsets.
    g.result_set = result_set
    g.result_set_raw = result_set_raw
    g.result_sets = legal_result_sets

# Set the resultset cookie after this request.
@app.after_request
def set_result_set(response):
    import binascii
    if g.result_set is not None:
        response.set_cookie('result_set', g.result_set, path='/')
    return response
