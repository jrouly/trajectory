"""
trajectory/utils/common.py
Author: Jean Michel Rouly

Define a collection of useful utility functions.
"""


def row2dict(row):
    """
    Convert a SQLAlchemy row to a dictionary.
    """
    return {
        col.name: getattr(row, col.name)
        for col in row.__table__.columns
    }


def jaccard(a, b):
    """
    Calculate the jaccard coefficient of two lists.
    """

    n = len(a.intersection(b))
    d = float(len(a) + len(b) - n)
    if d == 0:
        return 1
    return n / d


def topic_list(item=None, result_set=None):
    """
    Retrieve the ordered list of all topics represented by some item. If no
    item is requested, return the global list of topics. Optional filter by
    a result set.

    item can be a University, Department, or Course.
    """

    from trajectory.models import University, Department, Course, Topic
    from trajectory.models import CourseTopicAssociation
    from trajectory.models.meta import session

    # Generate the initial query. Note that if a result_set instance is
    # passed in, it will be used to filter the global topics.
    topics_query = session.query(Topic).order_by(Topic.id)
    if result_set is not None:
        topics_query = topics_query.filter(Topic.result_set_id==result_set.id)

    # If there was no item specifically requested, just return the global
    # topic set.
    if item is None:
        return topics_query.all()

    # Start constructing the per-item topic list.
    item_topics = topics_query.join(CourseTopicAssociation).join(Course)

    # Add any additional filtration for course/department/university.
    if type(item) == Course:
        item_topics = item_topics \
                .filter(Course.id==item.id) \
                .all()

    elif type(item) == Department:
        item_topics = item_topics \
                .join(Department) \
                .filter(Department.id==item.id) \
                .all()

    elif type(item) == University:
        item_topics = item_topics \
                .join(Department) \
                .join(University) \
                .filter(University.id==item.id) \
                .all()

    else:
        raise RuntimeError("Unknown item type requested.")

    return item_topics

def topic_vector(item=None, result_set=None):
    """
    Generate a vector indicating which topics are represented by the given
    item. If item is None, return a topic vector representing the global
    topic set (all 1s).

    item can be a University, Department, or Course.
    """

    from trajectory.models import University, Department, Course, Topic
    from trajectory.models import CourseTopicAssociation
    from trajectory.models.meta import session
    from bitarray import bitarray

    # Grab a reference to the list of all topics (in this result set, if
    # one was requested).
    global_topics = topic_list(result_set=result_set)

    # Construct the vector.
    vector = bitarray(len(global_topics))
    vector.setall(False)

    # If no item wsa specifically requested, return a bitarray of all True.
    if item is None:
        vector.setall(True)
        return vector

    # Grab a reference to the list of topics represented in the requested
    # item.
    item_topics = topic_list(item, result_set)

    # Set the bits where the topic is found.
    for it in item_topics:
        if it in global_topics:
            vector[global_topics.index(it)] = True

    return vector


def euclidean_distance(a,b):
    """
    Calculate the euclidean distance between two vectors.
    """

    import numpy
    a = numpy.array(list(a), dtype=int)
    b = numpy.array(list(b), dtype=int)
    return numpy.linalg.norm(a-b)


def cosine_similarity(a,b):
    """
    Calculate the cosine similarity between two vectors.
    """

    import numpy
    a = numpy.array(list(a), dtype=int)
    b = numpy.array(list(b), dtype=int)
    n = numpy.dot(a,b)
    d = numpy.linalg.norm(a,ord=2) * numpy.linalg.norm(b,ord=2)
    return 1.0 - n/d
