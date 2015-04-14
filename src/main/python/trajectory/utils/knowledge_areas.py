"""
trajectory/utils/knowledge_areas.py
Author: Jean Michel Rouly

Define a collection of tools to manipulate and retrieve information about
knowledge areas.
"""


def predicted_knowledge_areas(course, result_set=None):
    """
    Compute the set of ACM knowledge areas assigned to this course by
    determining conceptual overlap between the target course and the
    knowledge areas' inferred topics.
    """

    from trajectory.utils.vector import topic_list
    from trajectory.models import University, Department, Course
    from trajectory.models.meta import session

    # Handle empty case.
    if course is None:
        return []

    # Query database for knowledge areas.
    knowledge_areas = session.query(Department).join(University)\
            .filter(University.abbreviation=="ACM")\
            .filter(Department.abbreviation=="KA")\
            .first()

    # Handle case where ACM/KA is not present in the database.
    if knowledge_areas is None:
        raise RuntimeError("Knowledge areas not defined.")

    # This is the list of course objects representing knowledge areas.
    knowledge_areas = knowledge_areas.courses
    knowledge_areas_by_topic = {
            ka:set(topic_list(ka))
            for ka in knowledge_areas
    }

    course_topics = set(topic_list(course))

    # Generate the list of knowledge areas with conceptual overlap.
    inferred_knowledge_areas = set([
            ka for ka in knowledge_areas_by_topic
            if course_topics.intersection(knowledge_areas_by_topic[ka])
    ])

    return inferred_knowledge_areas


def ground_truth_knowledge_areas(course, result_set=None):
    """
    Look up the set of ground truth manually annotated knowledge areas for
    a course. If none are found, simply return an empty list.
    """

    return ["bar", "foo"]
