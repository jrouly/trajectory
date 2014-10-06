"""
vectorize.py
Author: Michel Rouly

Take a bag-of-words input file and vectorize it as a count vector, then
transform into a tf-idf vector.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn import cluster
from datetime import datetime
from time import time

import numpy
import logging
import os



def main():

    timestamp = datetime.strftime( datetime.now(), "%s" )
    logging.basicConfig(level=logging.DEBUG)
    logging.info( "Begin vectorization." )

    path = "../../data/gmu"

    max_df = 0.5     # terms must occur in under X documents
    min_df = 2       # terms must occur in at least X documents

    # First we build the corpus of documents.
    files = [os.path.join(root, name)
             for root, dirs, files in os.walk( path )
             for name in files
             if name.endswith(".txt")]

    corpus = []
    labels = []

    # Stick each file's content into the corpus
    for datafile in files:
        with open(datafile, 'r') as socket:
            content = socket.read()
            corpus.append( content )
            labels.append( os.path.basename( socket.name ) )

    # Vectorize according to TFIDF
    tfidf_vectorizer = TfidfVectorizer(
        input="content",        # will pass input directly
        encoding="ascii",       # use basic ascii encoding
        decode_error="ignore",  # ignore decoding errors
        strip_accents="ascii",  # strip fancy characters
        stop_words="english",   # remove english stopwords
        lowercase=True,         # lowercase everything
        use_idf=True,           # inverse document frequency (weighting)
        smooth_idf=True,        # smooth the data out

        max_df=max_df,          # terms must occur in under X documents
        min_df=min_df,          # terms must occur in at least X documents
    )

    vectorized_corpus = tfidf_vectorizer.fit_transform( corpus )

    logging.info("Data vectorized.")
    logging.info("  Number of entries:    %d." % vectorized_corpus.shape[0])
    logging.info("  Number of features:   %d." % vectorized_corpus.shape[1])
    logging.info("  Number of categories: %d." % len( set( labels ) ) )

    # Begin clustering
    logging.info("Begin clustering.")

    true_k = numpy.unique(labels).shape[0]
    true_k = 20

    km = cluster.MiniBatchKMeans(

        n_clusters = true_k,    # expected number of clusters

        #init="kmeans++",               # initialization method (smart)
        n_init=1,                      # number of random retries
        #init_size=300,
        #batch_size=100
    )

    # Time the operation
    t0 = time()
    km.fit(vectorized_corpus)
    t1 = time()

    # Perform metrics
    runtime         = (t1 - t0)
    homogeneity     = metrics.homogeneity_score(   labels, km.labels_ )
    completeness    = metrics.completeness_score(  labels, km.labels_ )
    v_measure       = metrics.v_measure_score(     labels, km.labels_ )
    adjusted_rand   = metrics.adjusted_rand_score( labels, km.labels_ )
    adjusted_mutual = metrics.adjusted_mutual_info_score( labels, km.labels_ )

    # Output to logs
    logging.info("  |-        Execution time: %fs"   % runtime)
    logging.info("  |-           Homogeneity: %0.3f" % homogeneity)
    logging.info("  |-          Completeness: %0.3f" % completeness)
    logging.info("  |-             V-measure: %0.3f" % v_measure)
    logging.info("  |-   Adjusted Rand-Index: %.3f"  % adjusted_rand)
    logging.info("  |-  Adjusted Mutual Info: %.3f"  % adjusted_mutual)

    # Display analysis
    logging.info("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = tfidf_vectorizer.get_feature_names()
    for i in range(true_k):
        logging.info("Cluster %d:" % i)
        for ind in order_centroids[i, :10]:
            logging.info(' %s' % terms[ind])


if __name__ == '__main__':
    main()
