"""
trajectory/utils.py
Author: Jean Michel Rouly

Define a collection of useful utility functions for performing analysis.
"""


def get_prereq_graph(course_id, layout=False, format=None, root=None):
    """
    Generate a graph of prerequisites within a course.

    layout -- whether or not to apply a layout to this graph.
    format -- what formatting to apply to the output
                None: return a NetworkX graph
                node: json formatted as node-link style
                adjacency: json formatted as adjacency style
                tree: json formatted as tree style
    root -- if tree formatting is requested, root of the tree
    """

    from trajectory.models import Department, Course
    from trajectory.models.meta import session

    from networkx.readwrite import json_graph
    import networkx as nx
    import json

    if format not in [None, "node", "adjacency", "tree"]:
        raise RuntimeError("Unknown requested data format %s" % format)

    # Initialize a new NetworkX graph.
    G = nx.DiGraph()

    # Attempt to look up the requested course.
    course = session.query(Course).get(course_id)
    if course is None:
        return None

    # Generate the prereq tree for the requested course.
    prereq_tree = get_prereq_tree(course_id)

    # Recursively add course ids in a subtree to the graph.
    def add_subtree(G, tree, parent=None):
        cid = tree[0]   # unpack information
        prereqs = tree[1]  # unpack information
        course = session.query(Course).get(cid)
        G.add_node(cid, row2dict(course)) # add this course
        # add an edge from the parent to this course
        if parent is not None:
            G.add_edge(parent, cid, label="prerequisite")
        # loop over prereq trees and recursively add them in
        for prereq in prereqs:
            add_subtree(G, prereq, cid)

    # Navigate the prerequisite tree and add the course ids as nodes, and
    # prerequisite relationships as unweighted edges.
    add_subtree(G, prereq_tree)

    # If a layout is requested, then calculate and apply it.
    if layout:
        pos = nx.spring_layout(G)
        for node in G.nodes():
            G.node[node]["viz"] = {
                'position': {
                    'x': pos[node][0],
                    'y': pos[node][1]
                }
            }

    if G is None:
        return G

    # Apply any requested data output formatting.

    if format == "node":
        return json.dumps(json_graph.node_link_data(G))
    elif format == "adjacency":
        return json.dumps(json_graph.adjacency_data(G))
    elif format == "tree":
        if root is None: # Ensure a root is specified.
            raise RuntimeError("No root specified in a tree formatted request.")
        return json.dumps(json_graph.tree_data(G, int(root)))
    else:
        return G

def get_prereq_tree(course_id, parents=set()):
    """
    Recursively identify the prerequisite chain of a course.  This tree is
    rooted at the requested parent course and is structured as a tuple of
    tuples.

    Ex:
    (a [
      (b, [ ])   prereq of a
      (c, [      prereq of a
        (d, [])  prereq of c
        (e, [])  prereq of c
      ])
    ])
    """

    from trajectory.models import Course
    from trajectory.models.meta import session

    # Attempt to identify the parent course.
    course = session.query(Course).get(course_id)
    if course is None:
        return None

    # Recursive depth base case.
    if course_id in parents:
        return None
    else:
        parents = parents | {course_id}

    # Base case.
    if len(course.prerequisites) == 0:
        return (course.id, [])

    # Recursive call.
    builder = []
    for prerequisite in course.prerequisites:
        sub_prereqs = get_prereq_tree(prerequisite.id, parents)
        if sub_prereqs is not None:
            builder.append(sub_prereqs)

    # Add recursively determined list.
    return (course.id, builder)


def get_prereq_set(course_id):
    """
    Get the set of prerequisite courses for a requested course. That is, a
    flat set with no repeats. This set does not contain the requested
    course.
    """

    # Attempt to identify a reference to the requested course.
    prereq_tree = get_prereq_tree(course_id)
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


def row2dict(row):
    """
    Convert a SQLAlchemy row to a dictionary.
    """
    return {
        col.name: getattr(row, col.name)
        for col in row.__table__.columns
    }

