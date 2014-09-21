"""
vectorize.py
Author: Michel Rouly

Take a bag-of-words input file and vectorize it as a count vector, then
transform into a tf-idf vector.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
import logging
import os



def main():

    timestamp = datetime.strftime( datetime.now(), "%s" )
    logging.basicConfig(level=logging.DEBUG)
    logging.info( "Begin vectorization." )

    path = "../../data/gmu"

    max_df = 10     # terms must occur in under X documents
    min_df = 5      # terms must occur in at least X documents

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
            labels.append( socket.name )

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

    km = cluster.MiniBatchKMeans(

        n_clusters = len(set(labels)), # expected number of clusters

        #init="kmeans++",               # initialization method (smart)
        #n_init=3,                      # number of random retries
        #init_size=300,
        #batch_size=100
    )

    # Time the operation
    t0 = time()
    clusterer.fit(data)
    t1 = time()

    # Perform metrics
    runtime         = (t1 - t0)
    homogeneity     = metrics.homogeneity_score(   labels, clusterer.labels_ )
    completeness    = metrics.completeness_score(  labels, clusterer.labels_ )
    v_measure       = metrics.v_measure_score(     labels, clusterer.labels_ )
    adjusted_rand   = metrics.adjusted_rand_score( labels, clusterer.labels_ )
    adjusted_mutual = metrics.adjusted_mutual_info_score( labels,
                                                          clusterer.labels_ )

    # Output to logs
    logging.info("  |-        Execution time: %fs"   % runtime)
    logging.info("  |-           Homogeneity: %0.3f" % homogeneity)
    logging.info("  |-          Completeness: %0.3f" % completeness)
    logging.info("  |-             V-measure: %0.3f" % v_measure)
    logging.info("  |-   Adjusted Rand-Index: %.3f"  % adjusted_rand)
    logging.info("  |-  Adjusted Mutual Info: %.3f"  % adjusted_mutual)

if __name__ == '__main__':
    main()
