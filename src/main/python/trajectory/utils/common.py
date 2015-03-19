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


def topic_vector(item, result_set=None):
    """
    Generate a vector indicating which topics are represented by the given
    item.

    item can be a University, Department, or Course.
    """

    from trajectory.models import University, Department, Course, Topic
    from trajectory.models import CourseTopicAssociation
    from trajectory.models.meta import session
    from bitarray import bitarray

    # Generate the initial query. Note that if a result_set instance is
    # passed in, it will be used to filter the global topics.
    topics_query = session.query(Topic).order_by(Topic.id)
    if result_set is not None:
        topics_query = topics_query.filter(Topic.result_set_id==result_set.id)
    global_topics = topics_query.all()

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
        raise RuntimeError("Unknown item type for topic vector.")

    # Construct the vector.
    vector = bitarray(len(global_topics))
    vector.setall(False)

    # Set the bits where the topic is found.
    for it in item_topics:
        if it in global_topics:
            vector[global_topics.index(it)] = True

    return vector
