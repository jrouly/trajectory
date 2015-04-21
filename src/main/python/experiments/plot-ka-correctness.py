from trajectory.utils.knowledge_areas import ground_truth_knowledge_areas
from trajectory.utils.knowledge_areas import predicted_knowledge_areas
from trajectory.utils.vector import jaccard
from trajectory.models.meta import session
from trajectory.models import Course, Department, University, Topic, ResultSet

import numpy, csv

print("Begin.")

print("Read from database...")
gmu_cs = session.query(Department).filter(Department.abbreviation=="CS")\
                .join(University).filter(University.abbreviation=="GMU")\
                .first()
gmu = gmu_cs.university
result_sets = session.query(ResultSet).all()
print("Done.")

print("Compute predicted and truth knowledge areas...")
knowledge_areas = [
        {
            'predicted': {
                course.id: predicted_knowledge_areas(course, rs)
                for course in gmu_cs.courses
            },
            'truth': {
                course.id: ground_truth_knowledge_areas(course)
                for course in gmu_cs.courses
            },
        } for rs in result_sets
]
print("Done.")

print("Calculate jaccard and percent metrics...")
for ka_dict in knowledge_areas:
    ka_dict['jaccard'] = {
            course.id: jaccard(
                ka_dict['predicted'][course.id],
                ka_dict['truth'][course.id]
            ) for course in gmu_cs.courses
            if None not in [
                ka_dict['predicted'][course.id],
                ka_dict['truth'][course.id]
            ]
    }
    ka_dict['percent'] = {
            course.id: len(set(ka_dict['predicted'][course.id])\
                            .intersection(set(ka_dict['truth'][course.id])))\
                        / len(ka_dict['truth'][course.id])
            for course in gmu_cs.courses
            if ka_dict['truth'][course.id]
    }
print("Done.")

print("Calculate average percent and jaccard metrics...")
for ka_dict in knowledge_areas:
    ka_dict['average_percent'] = numpy.mean(list(ka_dict['percent'].values()))
    ka_dict['average_jaccard'] = numpy.mean(list(ka_dict['jaccard'].values()))
print("Done.")

csv_out = [{
        "ResultSetID": rs.id,
        "Alpha": rs.alpha,
        "Beta": rs.beta,
        "Iterations": rs.iterations,
        "Topics": rs.num_topics,
        "AverageJaccard": knowledge_areas[rs.id-1]['average_jaccard'],
        "AveragePercent": knowledge_areas[rs.id-1]['average_percent'],
} for rs in result_sets]

fp = open("ka-correctness.csv", "w")
headers = [
    "ResultSetID",
    "Alpha",
    "Beta",
    "Iterations",
    "Topics",
    "AverageJaccard",
    "AveragePercent",
]
writer = csv.DictWriter(fp, fieldnames=headers)
writer.writeheader()
writer.writerows(csv_out)
fp.close()

print("Success.")
