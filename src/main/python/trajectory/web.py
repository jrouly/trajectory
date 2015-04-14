from flask import Flask, g, render_template, url_for, abort
from flask import make_response, request
from jinja2 import FileSystemLoader
from sqlalchemy.sql.expression import func
import itertools
import pickle

from trajectory import config as TRJ
from trajectory.utils.prereqs import get_prereq_graph
from trajectory.utils.vector import jaccard, topic_list, topic_vector
from trajectory.utils.vector import cosine_similarity, euclidean_distance
from trajectory.utils.knowledge_areas import predicted_knowledge_areas
from trajectory.utils.knowledge_areas import ground_truth_knowledge_areas
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

# Define routing for university index pages.
@app.route('/universities/')
@app.route('/universities/<string:u>/')
def university(u=None):

    # If no university is requested, just serve up the uni list page.
    if u is None:
        universities = app.db.query(University).all()
        return render_template("university_list.html",
                universities=universities)

    # If a university is requested, try to find it.
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
    departments = app.db.query(Department).all()
    return render_template("department.html",
            department=department,
            departments=departments)

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
            course=course,
            topics=topic_list(course, result_set=g.result_set_raw))

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
@app.route('/prereqs/<string:cid>/<string:format>')
def prereq_tree(cid, format="node"):
    # Attempt to retreive data in the requested format.
    try:
        data = get_prereq_graph(cid, format=format)
    except RuntimeError:
        abort(404)
    if data is None:
        abort(404)
    response = make_response(data)
    response.headers["Content-Type"] = "text/plain"
    return response

# Define routing for department comparison page.
@app.route('/compare/')
@app.route('/compare/<string:daid>/<string:dbid>/')
def compare_departments(daid=None, dbid=None):

    if None in [daid, dbid]:
        departments = app.db.query(Department).all()
        return render_template("compare_departments_landing.html",
                departments=departments)

    # Look up references to requested departments.
    department_a = app.db.query(Department).get(daid)
    department_b = app.db.query(Department).get(dbid)

    # If either department isn't found, or if there is no result set
    # (meaning no topics to infer) then simply 404.
    if department_a is None or department_b is None or g.result_set_raw is None:
        abort(404)

    # Identify a set of topics for each department.
    department_a_topics = set(topic_list(department_a, g.result_set_raw))
    department_b_topics = set(topic_list(department_b, g.result_set_raw))

    # Generate topic vectors for the two departments.
    a_vector = topic_vector(department_a, g.result_set_raw)
    b_vector = topic_vector(department_b, g.result_set_raw)
    a_vector_string = a_vector.unpack(one=b'1', zero=b'0').decode('utf-8')
    b_vector_string = b_vector.unpack(one=b'1', zero=b'0').decode('utf-8')

    # Run similarity metrics.
    similarity = dict()
    similarity['jaccard'] = {
            'name': 'Jaccard Index',
            'range': '[0, 1]',
            'description': 'Comparative set cardinality.',
            'value': jaccard(department_a_topics, department_b_topics),
    }
    similarity['cosine'] = {
            'name': 'Cosine Similarity',
            'range': '[-1, 1]',
            'description': 'Geometric cosine distance.',
            'value': cosine_similarity(a_vector, b_vector),
    }
    similarity['euclidean'] = {
            'name': 'Euclidean Distance',
            'description': 'Geometric vector distance.',
            'value': euclidean_distance(a_vector, b_vector),
    }

    # Remove common topics from the topic sets.
    intersection = department_a_topics.intersection(department_b_topics)
    department_a_topics = department_a_topics - intersection
    department_b_topics = department_b_topics - intersection

    # Number of courses in each department.
    num_courses_a = app.db.query(Course).join(Department) \
            .filter(Department.id==daid).count()
    num_courses_b = app.db.query(Course).join(Department) \
            .filter(Department.id==dbid).count()

    # Global list of departments for switching over.
    departments = app.db.query(Department).all()

    return render_template("compare_departments.html",
            da=department_a,
            db=department_b,

            da_topics=department_a_topics,
            db_topics=department_b_topics,

            num_courses_a=num_courses_a,
            num_courses_b=num_courses_b,

            common_topics=intersection,

            departments=departments,

            similarity_metrics=similarity,

            da_vector=a_vector_string,
            db_vector=b_vector_string,
    )

# Define routing for departmental evaluation tool.
@app.route('/evaluate/')
@app.route('/evaluate/<string:u>/<string:d>/')
def evaluation(u=None, d=None):

    if u is None or d is None:
        return render_template("evaluate_landing.html")

    department = app.db.query(Department).join(University) \
            .filter(University.abbreviation==u) \
            .filter(Department.abbreviation==d) \
            .first()
    if department is None:
        abort(404) # department not found

    # Retrieve the set of predicted and ground truth knowledge area labels
    # for each course.
    try:
        knowledge_areas = {
                'predicted': {
                    course.id: predicted_knowledge_areas(
                                        course,
                                        result_set=g.result_set_raw)
                        for course in department.courses
                },
                'truth': {
                    course.id: ground_truth_knowledge_areas(
                                        course,
                                        result_set=g.result_set_raw)
                        for course in department.courses
                },
        }
    except RuntimeError:
        # Return empty knowledge area lists if an error is encountered.
        knowledge_areas = {
            'predicted': {course.id: [] for course in department.courses},
            'truth': {course.id: [] for course in department.courses},
        }

    # Calculate the jaccard coefficient of the prediction/truth sets, use
    # this as a 'correctness' metric.
    knowledge_areas['jaccard'] = {
            course.id: jaccard(
                knowledge_areas['predicted'][course.id],
                knowledge_areas['truth'][course.id]
            ) for course in department.courses
    }

    return render_template("evaluate_department.html",
            department=department,
            knowledge_areas=knowledge_areas,)


################################
# Custom Filters and Functions #
################################

@app.template_filter('ka_parse')
def knowledge_area_abbreviation(ka):
    """
    Given an ACM knowledge area, split it up by its Abbreviation (eg. AL)
    and its Title (eg. Algorithms and Complexity). This is done by
    isolating the location of the abbreviation in the title string (where
    the first left paren occurs) and only including the subsequent
    characters.
    """

    return {
            'abbr': ka.title,
            'title': ka.title[ka.title.find('(')+1:-1]
    }

@app.template_filter('course_count')
def course_count(data):
    if type(data) == University:
        return app.db.query(Course).join(Department).join(University) \
                .filter(University.id==data.id).count()
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
