from trajectory.models.meta import session
from trajectory.models import Course, Topic, CourseTopicAssociation, Department, University, ResultSet

from itertools import chain
import numpy

def weighted_topic_vector(course, result_set):
    topic_vector = []
    global_topics = session.query(Topic).filter(Topic.result_set==result_set).all()
    course_topics = [ta.topic for ta in course.topics if ta.topic.result_set==result_set]
    course_topic_assocs = [ta for ta in course.topics if ta.topic.result_set==result_set]

    for topic in global_topics:
        if topic not in course_topics:
            topic_vector.append(0)
        else:
            topic_index = course_topics.index(topic)
            proportion = course_topic_assocs[topic_index].proportion
            topic_vector.append(proportion)

    return topic_vector


def prerequisite_distances(course, result_set):
    course_vector = numpy.array(weighted_topic_vector(course, result_set))
    prerequisite_vectors = [numpy.array(weighted_topic_vector(prereq, result_set)) for prereq in course.prerequisites]
    return [1 - numpy.linalg.norm(course_vector - prereq_vector) for prereq_vector in prerequisite_vectors]

def university_prerequisite_statistics(abbreviation, result_set):
    uni_courses = session.query(Course).join(Department).join(University).filter(University.abbreviation==abbreviation).all()
    prereq_distances = [prerequisite_distances(course, result_set) for course in uni_courses]
    prereq_distances = [p for p in prereq_distances if p] # strip courses with no prerequisites
    mean = numpy.mean(list(chain.from_iterable(prereq_distances)))
    stdv = numpy.std(list(chain.from_iterable(prereq_distances)))
    return (mean, stdv)

rs51 = session.query(ResultSet).get(51)
result_sets = session.query(ResultSet).all()

#universities = session.query(University).all()
#for uni in universities:
#    (mean, stdv) = university_prerequisite_statistics(uni.abbreviation, rs51)
#    print("%s Mean: %0.3f Std: %0.3f" % (uni.abbreviation, mean, stdv))
