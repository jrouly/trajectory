"""
trajectory/utils/prereqs.py
Author: Jean Michel Rouly

Define a collection of useful utility functions for analyzing course and
departmental prerequisite structures.
"""


def get_prereq_graph(course_id, format=None):
    """
    Generate a graph of prerequisites within a course. If format is not
    requested, simply return a NetworkX graph object.

    couse_id: the ID of the requested course
    format:   what format to return in (optional)
                  node: json formatted as node-link style
                  adjacency: json formatted as adjacency style
                  tree: json formatted as tree style
    """

    from trajectory.models import Department, Course
    from trajectory.models.meta import session
    from trajectory.utils.common import row2dict

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

    # Recursively add course ids in a subtree to the graph.
    def add_tree(G, tree, parent=None):
        cid = tree[0]   # unpack information
        prereqs = tree[1]  # unpack information
        course = session.query(Course).get(cid)

        # Insert all known data, including department abbreviation.
        node_data = row2dict(course)
        node_data['dept'] = course.department.abbreviation

        # Identify the primary course in the graph (the requested).
        if str(cid) == str(course_id):
            node_data['prime'] = True
        else:
            node_data['prime'] = False

        # If the course has already been added, generate a unique ID for it
        # based on its parent, and add it anyway. But don't recurse into
        # its list of prereqs.
        seen = False
        if cid in G.nodes():
            cid = str(parent) + "-" + str(cid)
            seen = True

        # Add course and an edge from its parent, if relevant.
        G.add_node(cid, node_data)
        if parent is not None:
            G.add_edge(parent, cid)

        # Recurse through the prerequisite tree and add in subtrees.
        if not seen:
            for prereq in prereqs:
                add_tree(G, prereq, cid)

    # Navigate the prerequisite tree and add the course ids as nodes, and
    # prerequisite relationships as unweighted edges.
    prereq_tree = get_prereq_tree(course_id)
    add_tree(G, prereq_tree)

    if G is None:
        return G

    # Calculate and apply a basic layout.
    pos = nx.spring_layout(G)
    for node in G.nodes():
        G.node[node]["viz"] = {
            'position': {
                'x': pos[node][0],
                'y': pos[node][1]
            }
        }

    # Apply any requested data output formatting.
    if format == "node":
        return json.dumps(json_graph.node_link_data(G))
    elif format == "adjacency":
        return json.dumps(json_graph.adjacency_data(G))
    elif format == "tree":
        return json.dumps(json_graph.tree_data(G, int(course_id)))
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
