from trajectory.models.meta import session
from trajectory.models import Course, Department, University, ResultSet
from trajectory.utils.vector import jaccard, topic_list
import numpy

result_sets = session.query(ResultSet).all()
rs = session.query(ResultSet).get(51)

departments = session.query(Department).all()
departments = list(filter(lambda department:
        not ((department.university.abbreviation=="ACM" and department.abbreviation=="KA") or
             (department.university.abbreviation=="GMU" and department.abbreviation=="AIT")),
        departments))

def compare(depA, depB, rs):
    dep_a_topics = topic_list(depA, rs)
    dep_b_topics = topic_list(depB, rs)
    return jaccard(dep_a_topics, dep_b_topics)

comparisons = {}

for depA in departments:
    print(depA.university.abbreviation)
    comparisons[depA] = {}
    for depB in departments:
        #values = [compare(depA, depB, rs) for rs in result_sets]
        #value = numpy.mean(values)
        value = compare(depA, depB, rs)
        comparisons[depA][depB] = value

print("done")

print("\t", end='\t')
for dep in departments:
    print(dep.university.abbreviation, end=',')
print()

for depA in departments:
    for depB in departments:
        print("%0.3f" % comparisons[depA][depB], end=',')
    print()
