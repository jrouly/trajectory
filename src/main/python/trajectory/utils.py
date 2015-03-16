"""
trajectory/utils.py
Author: Jean Michel Rouly

Define a collection of useful utility functions for performing analysis.
"""


def get_prereq_graph(department_id):
    """
    Generate a graph of prerequisites within a department.
    """

    from trajectory.models import Department, Course
    from trajectory.models.meta import session
    import networkx as nx

    # Initialize a new NetworkX graph.
    G = nx.DiGraph()

    # Attempt to look up the requested department.
    department = session.query(Department).get(department_id)
    if department is None:
        return G

    # Look up the list of all parents to generate trees for.
    course_ids = [c.id for c in department.courses]

    # Generate the prereq trees for each course in the department.
    # This is inefficient and duplicates data. TODO: make it not so.
    prereq_forest = [get_prereq_tree(cid) for cid in course_ids]

    print_cid = lambda cid: print(session.query(Course).get(cid))

    # Recursively add course ids in a subtree to the graph.
    def add_subtree(G, tree, parent=None):
        course = tree[0]   # unpack information
        prereqs = tree[1]  # unpack information
        G.add_node(course) # add this course
        # add an edge from the parent to this course
        if parent is not None:
            G.add_edge(parent, course)
        # loop over prereq trees and recursively add them in
        for prereq in prereqs:
            add_subtree(G, prereq, course)

    # Navigate the prerequisite forest and add the course ids as nodes, and
    # prerequisite relationships as unweighted edges.
    for tree in prereq_forest:
        add_subtree(G, tree)

    return G

def get_prereq_tree(course_id, depth=1):
    """
    Recursively identify the prerequisite chain of a course. Maximum depth
    of 50 prerequisites in a chain, and error out if this limit is
    exceeded.

    This tree is rooted at the requested parent course and is structured as
    a tuple of tuples.

    Ex:
    (a [
      (b, [ ])   prereq of a
      (c, [      prereq of a
        (d, [])  prereq of c
        (e, [])  prereq of c
      ])
    ])
    """

    if depth > 50:
        raise RuntimeError("Maximum recursive depth exceeded.")

    from trajectory.models import Course
    from trajectory.models.meta import session

    # Attempt to identify the parent course.
    course = session.query(Course).get(course_id)
    if course is None:
        return None

    # Base case.
    if len(course.prerequisites) == 0:
        return (course.id, [])

    # Recursive call.
    builder = []
    for prerequisite in course.prerequisites:
        sub_prereqs = get_prereq_tree(prerequisite.id, depth+1)
        builder.append(sub_prereqs)

    # Add recursively determined list.
    return (course.id, builder)


def get_prereq_set(course_id, depth=1):
    """
    Get the set of prerequisite courses for a requested course. That is, a
    flat set with no repeats. This set does not contain the requested
    course.
    """

    # Attempt to identify a reference to the requested course.
    prereq_tree = get_prereq_tree(course_id, depth=depth)
    if prereq_tree is None:
        return set()

    # Flatten function of an arbitrarily deeply nested list of lists.
    def flatten(container):
        for i in container:
            if isinstance(i, list) or isinstance(i, tuple):
                for j in flatten(i):
                    yield j
            else:
                yield i

    # Remove duplicates.
    return set(flatten(prereq_tree)) - {course_id}
