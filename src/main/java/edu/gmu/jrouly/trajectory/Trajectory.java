package edu.gmu.jrouly.trajectory;

import java.io.File;
import java.io.IOException;
import java.io.FileFilter;
import java.io.FileWriter;
import java.io.PrintWriter;

import java.text.SimpleDateFormat;

import java.net.URI;

import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.util.ArrayList;
import java.util.Date;
import java.util.Formatter;
import java.util.Map;
import java.util.Iterator;
import java.util.Locale;
import java.util.TreeSet;
import java.util.regex.Pattern;

import cc.mallet.pipe.CharSequence2TokenSequence;
import cc.mallet.pipe.Input2CharSequence;
import cc.mallet.pipe.Pipe;
import cc.mallet.pipe.SerialPipes;
import cc.mallet.pipe.TokenSequence2FeatureSequence;
import cc.mallet.pipe.TokenSequenceLowercase;
import cc.mallet.pipe.TokenSequenceRemoveStopwords;
import cc.mallet.pipe.iterator.FileIterator;

import cc.mallet.topics.ParallelTopicModel;
import cc.mallet.topics.TopicAssignment;
import cc.mallet.topics.TopicInferencer;

import cc.mallet.types.Alphabet;
import cc.mallet.types.FeatureSequence;
import cc.mallet.types.IDSorter;
import cc.mallet.types.Label;
import cc.mallet.types.LabelSequence;
import cc.mallet.types.LabelVector;
import cc.mallet.types.InstanceList;
import cc.mallet.types.Instance;

import edu.gmu.jrouly.trajectory.CLI;

/**
 * The main executable class of the trajectory project to perform topic
 * modeling.
 */
public class Trajectory {

  // Debug flag status.
  private static boolean debug;

  // I/O directories.
  private static File inDirectory = null;
  private static File outDirectory = null;

  // Number of threads to use for the parallel model.
  private static final int DEFAULT_NUM_THREADS = 2;
  private static int numThreads = DEFAULT_NUM_THREADS;

  // Number of iterations to use when training the model.
  private static final int DEFAULT_NUM_ITERATIONS = 50;
  private static int numIterations = DEFAULT_NUM_ITERATIONS;

  // Number of expected topics to use when modeling.
  // TODO: Find a better way to auto initialize this variable.
  private static final int DEFAULT_NUM_TOPICS = 50;
  private static int numTopics = DEFAULT_NUM_TOPICS;


  /**
   * Read input from the command line and execute an LDA topic model over a
   * given set of data according to user defined constraints.
   */
  public static void main( String[] args ) {

    // Set command line flags and values.
    System.out.println( "> Parsing command line arguments." );
    parseArgs( args );

    // Generate data processing pipeline.
    System.out.println( "> Building data processing pipeline." );
    Pipe pipe = buildPipe();

    // Get list of targets in data directory.
    System.out.println( "> Establishing data targets." );
    File[] targets = inDirectory.listFiles();

    // Get an iterator over data targets.
    System.out.println( "> Creating data iterator." );
    FileIterator iterator = getDataIterator( targets );

    // Build an instance set from data targets.
    System.out.println( "> Creating data instances." );
    InstanceList instances = new InstanceList( pipe );
    instances.addThruPipe( iterator );

    // Create an LDA Topic Model.
    System.out.println( "> Initializing LDA Topic Model." );
    ParallelTopicModel model = buildModel( instances );

    // Train the Topic Model.
    System.out.println( "> Training LDA Topic Model." );

    try {
      model.estimate();
    } catch( IOException exp ) {
      // The model broke when reading in files.
      System.err.println( "> Error when reading from data set." );
      System.exit( 1 );
    }

    // Print out results in a CSV format.
    printResults(model);

    // Exit.
    System.out.println( "> Exit." );
    System.exit( 0 );
    return;

  }


  /**
   * Parse and extract values from user input command line arguments.
   *
   * @param args command line arguments
   * @see edu.gmu.jrouly.trajectory.CLI
   */
  private static void parseArgs( String[] args ) {

    // Parse the command line arguments.
    Map<String, String> argmap = CLI.parse( args );

    // If the "debug" argument is present, then its value is true.
    debug = argmap.containsKey( "debug" );

    // If the numThreads argument is present, grab its value.
    if( argmap.containsKey( "threads" ) ) {
      String numThreadsString = argmap.get( "threads" );
      numThreads = Integer.parseInt( numThreadsString );
    }

    // If the numIter argument is present, grab its value.
    if( argmap.containsKey( "iterations" ) ) {
      String numIterationsString = argmap.get( "iterations" );
      numIterations = Integer.parseInt( numIterationsString );
    }

    // If the numTopics argument is present, grab its value.
    if( argmap.containsKey( "topics" ) ) {
      String numTopicsString = argmap.get( "topics" );
      numTopics = Integer.parseInt( numTopicsString );
    }

    boolean default_out = true;
    try {

      // Grab and process the "in" path request.
      String requestedInPath = argmap.get( "in" );
      Path inPath = Paths.get( requestedInPath );
      inDirectory = inPath.toFile();

      // Grab and process the "out" path request.
      if( argmap.containsKey( "out" ) ) {
        default_out = false;
        String requestedOutPath = argmap.get( "out" );
        Path outPath = Paths.get( requestedOutPath );
        outDirectory = outPath.toFile();
      }

    } catch( InvalidPathException exp ) {

      // The user-suggested path was invalid.
      System.err.println( "> Unable to resolve the requested I/O paths." );
      System.exit( 1 );

    }

    // Verify that the cleaned data directory can be located on the disk.
    if( ! inDirectory.isDirectory() ) {
      System.err.println( "> Unable to resolve the input path \""
                          + inDirectory.toString() + "\"." );
      System.exit( 1 );
    } else if( ! default_out && ! outDirectory.isDirectory() ) {
      System.err.println( "> Unable to resolve the output path \""
                          + outDirectory.toString() + "\"." );
      System.exit( 1 );
    } else {
      System.out.println( "> Using input directory: "
                          + inDirectory.toString() );
      if( default_out )
        System.out.println( "> Directing output to standard out." );
      else
        System.out.println( "> Using output directory: "
                            + outDirectory.toString() );
    }

  }


  /**
   * Build a workflow pipe that cleans and tokenizes the input data.
   *
   * @return data processing workflow pipeline
   */
  private static Pipe buildPipe() {

    // Begin by importing documents from text.
    ArrayList<Pipe> pipeList = new ArrayList<Pipe>();

    // Pipes: lowercase, tokenize, remove stopwords, map to features.
    pipeList.add( new Input2CharSequence("UTF-8") );
    pipeList.add( new CharSequence2TokenSequence(
                          Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")) );
    pipeList.add( new TokenSequenceLowercase() );
    //pipeList.add( new TokenSequenceRemoveStopwords(false, false) );
    pipeList.add( new TokenSequence2FeatureSequence() );
    return new SerialPipes(pipeList);

  }


  /**
   * Given a list of directories, read in their contents and generate a
   * FileIterator over them (recurses into child directories).
   *
   * @param directories list of file pointers to data directories (per set)
   * @return iterator over data files
   */
  private static FileIterator getDataIterator( File[] directories ) {

    // Construct a file iterator recursing over the data directories that
    // only accepts files with the .txt extension.
    FileIterator iterator =
      new FileIterator( directories,
                        new FileFilter() {
                          @Override
                          public boolean accept(File file) {
                            return file.toString().endsWith(".txt") &&
                                   file.isFile();
                          }
                        },
                        FileIterator.LAST_DIRECTORY );

    return iterator;

  }


  /**
   * Create an untrained LDA Topic Model with the instance data.
   *
   * @param instances set of data instances
   * @return untrained LDA topic model
   */
  private static ParallelTopicModel buildModel( InstanceList instances ) {

    // Create the topic model.
    // 1st paremeter: number of topics
    // 2nd parameter: alpha sum, defaults to number of topics
    // 3rd parameter: beta, defaults to 0.01
    ParallelTopicModel model = new ParallelTopicModel( numTopics );

    // Set data instances.
    model.addInstances( instances );

    // Use two parallel samplers, which each look at one half the corpus and combine
    // statistics after every iteration.
    model.setNumThreads( numThreads );

    // Run the model for n iterations and stop.
    // For debugging, n=50 is a good number.
    // For real applications, use n=1000 to n=2000 iterations.
    model.setNumIterations( numIterations );

    return model;

  }


  // TODO: Make this not suck.
  private static void printResults(ParallelTopicModel model) {

    // Define a PrintWriter either to a new log file or default to standard
    // output.
    PrintWriter writer;
    if( outDirectory != null ) {
      try {
        Path outDirectoryPath = outDirectory.toPath();
        Path outFilePath = Paths.get(
          new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss")
            .format(new Date()) + ".log");
        outDirectory = outDirectoryPath.resolve(outFilePath).toFile();
        writer = new PrintWriter(new FileWriter(outDirectory), true);
      } catch( IOException io ) {
        // Default to standard output.
        System.err.println( "> Unable to access output directory, defaulting to standard out." );
        writer = new PrintWriter(System.out, true);
      }
    }
    else {
      // Default to standard output.
      writer = new PrintWriter(System.out, true);
    }

    System.out.println( "> Printing document key." );
    ArrayList<TopicAssignment> data = model.getData();
    for( int document = 0; document < data.size(); document++ ) {

      // Isolate the course ID (the filename minus the .txt extension).
      Object name = data.get(document).instance.getName();
      Path filepath = Paths.get((URI)name);
      String filename = filepath.getFileName().toString();
      String course = filename.substring(0, filename.lastIndexOf('.'));

      double[] topicProbabilities = model.getTopicProbabilities(document);
      writer.printf("%d, %s", document, course);

      for( int topic = 0; topic < topicProbabilities.length; topic++ ) {
        double proportion = topicProbabilities[topic];
        writer.printf(", %d, %f", topic, proportion);
      }
      writer.println();
    }
    writer.println(); // Add a newline after the first key.

    // Get top 10 words for each topic.
    System.out.println( "> Printing topic key." );
    Object[][] topics = model.getTopWords( 10 );
    for( int i = 0; i < topics.length; i++ ) {
      Object[] topic = topics[i]; // Get topic's word list.
      writer.printf( "%d", i );
      for( int j = 0; j < topic.length; j++ ) {
        String word = topic[j].toString();
        writer.printf( ", %s", word );
      }
      writer.println();
    }

    writer.flush();
  }




/* stuff {{{

    // Show the words and topics in the first instance

    // The data alphabet maps word IDs to strings
    Alphabet dataAlphabet = instances.getDataAlphabet();

    FeatureSequence tokens = (FeatureSequence) model.getData().get(0).instance.getData();
    LabelSequence topics = model.getData().get(0).topicSequence;

    // For each token in the 0th instance, print out the topic it is
    // associated with.
    Formatter out = new Formatter(new StringBuilder(), Locale.US);
    for (int position = 0; position < tokens.getLength(); position++) {
        out.format("%s-%d ", dataAlphabet.lookupObject(tokens.getIndexAtPosition(position)), topics.getIndexAtPosition(position));
    }
    System.out.println(out);

    // Estimate the topic distribution of the first instance,
    // given the current Gibbs state.
    double[] topicDistribution = model.getTopicProbabilities(0);

    // Get an array of sorted sets of word ID/count pairs
    ArrayList<TreeSet<IDSorter>> topicSortedWords = model.getSortedWords();

    // Show top 5 words in topics with proportions for the first document
    for (int topic = 0; topic < numTopics; topic++) {
        Iterator<IDSorter> iterator = topicSortedWords.get(topic).iterator();

        out = new Formatter(new StringBuilder(), Locale.US);
        out.format("%d\t%.3f\t", topic, topicDistribution[topic]);
        int rank = 0;
        while (iterator.hasNext() && rank < 5) {
            IDSorter idCountPair = iterator.next();
            out.format("%s (%.0f) ", dataAlphabet.lookupObject(idCountPair.getID()), idCountPair.getWeight());
            rank++;
        }
        System.out.println(out);
    }

    // Create a new instance with high probability of topic 0
    StringBuilder topicZeroText = new StringBuilder();
    Iterator<IDSorter> iterator = topicSortedWords.get(0).iterator();

    int rank = 0;
    while (iterator.hasNext() && rank < 5) {
        IDSorter idCountPair = iterator.next();
        topicZeroText.append(dataAlphabet.lookupObject(idCountPair.getID()) + " ");
        rank++;
    }

    // Create a new instance named "test instance" with empty target and source fields.
    InstanceList testing = new InstanceList(instances.getPipe());
    testing.addThruPipe(new Instance(topicZeroText.toString(), null, "test instance", null));

    TopicInferencer inferencer = model.getInferencer();
    double[] testProbabilities = inferencer.getSampledDistribution(testing.get(0), 10, 1, 5);
    System.out.println("0\t" + testProbabilities[0]);




    System.out.println();
    model.printDocumentTopics( new PrintWriter( System.out ), 0.0, 5 );



  }
}}} */


}
