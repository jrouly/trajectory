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
import cc.mallet.types.Labeling;
import cc.mallet.types.LabelAlphabet;
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
  private static Path inPath = null;
  private static Path outPath = null;

  // Number of threads to use for the parallel model.
  private static final int DEFAULT_NUM_THREADS = 2;
  private static int numThreads = DEFAULT_NUM_THREADS;

  // Number of iterations to use when training the model.
  private static final int DEFAULT_NUM_ITERATIONS = 50;
  private static int numIterations = DEFAULT_NUM_ITERATIONS;

  // Number of expected topics to use when modeling.
  private static final int DEFAULT_NUM_TOPICS = 50;
  private static int numTopics = DEFAULT_NUM_TOPICS;

  // Alpha sum parameter.
  private static final double DEFAULT_ALPHA_SUM = numTopics;
  private static double alphaSum = DEFAULT_ALPHA_SUM;

  // Beta parameter.
  private static final double DEFAULT_BETA = 0.01;
  private static double beta = DEFAULT_BETA;

  // Number of words to display in each topic on output.
  private static final int DEFAULT_NUM_WORDS = 10;
  private static int numWords = DEFAULT_NUM_WORDS;


  /**
   * Read input from the command line and execute an LDA topic model over a
   * given set of data according to user defined constraints.
   */
  public static void main(String[] args) {

    // Set command line flags and values.
    parseArgs(args);

    // Generate data processing pipeline.
    System.out.println("> Building data processing pipeline.");
    Pipe pipe = buildPipe();

    // Get list of targets in data directory.
    System.out.println("> Establishing data targets.");
    File[] targets = inPath.toFile().listFiles();

    // Get an iterator over data targets.
    System.out.println("> Creating data iterator.");
    FileIterator iterator = getDataIterator(targets);

    // Build an instance set from data targets.
    System.out.println("> Creating data instances.");
    InstanceList instances = new InstanceList(pipe);
    instances.addThruPipe(iterator);

    // Create an LDA Topic Model.
    System.out.println("> Initializing LDA Topic Model.");
    ParallelTopicModel model = buildModel(instances);

    // Train the Topic Model.
    System.out.println("> Training LDA Topic Model.");

    try {
      model.estimate();
    } catch(IOException exp) {
      // The model broke when reading in files.
      System.out.println("> Error when reading from data set.");
      System.exit(1);
    } catch(Exception e) {
      // Unknown error during estimation.
      System.out.println("> Unknown error during estimation.");
      e.printStackTrace();
      System.exit(1);
    }

    // Print out results in a CSV format.
    printResults(model);

    // Exit.
    System.out.println("> Exit.");
    System.exit(0);
    return;

  }


  /**
   * Parse and extract values from user input command line arguments.
   *
   * @param args command line arguments
   * @see edu.gmu.jrouly.trajectory.CLI
   */
  private static void parseArgs(String[] args) {

    // Parse the command line arguments.
    Map<String, String> argmap = CLI.parse(args);

    // If the "debug" argument is present, then its value is true.
    debug = argmap.containsKey("debug");

    // If the numThreads argument is present, grab its value.
    if(argmap.containsKey("threads")) {
      String numThreadsString = argmap.get("threads");
      numThreads = Integer.parseInt(numThreadsString);
    }

    // If the numIter argument is present, grab its value.
    if(argmap.containsKey("iterations")) {
      String numIterationsString = argmap.get("iterations");
      numIterations = Integer.parseInt(numIterationsString);
    }

    // If the alpha argument is present, grab its value.
    if(argmap.containsKey("alpha")) {
      String alphaString = argmap.get("alpha");
      alphaSum = Double.parseDouble(alphaString);
    }

    // If the beta argument is present, grab its value.
    if(argmap.containsKey("beta")) {
      String betaString = argmap.get("beta");
      beta = Double.parseDouble(betaString);
    }

    // If the numTopics argument is present, grab its value.
    if(argmap.containsKey("topics")) {
      String numTopicsString = argmap.get("topics");
      numTopics = Integer.parseInt(numTopicsString);
    }

    // If the numWords argument is present, grab its value.
    if(argmap.containsKey("words")) {
      String numWordsString = argmap.get("words");
      numWords = Integer.parseInt(numWordsString);
    }

    try {

      // Grab and process the "in" path request.
      String requestedInPath = argmap.get("in");
      inPath = Paths.get(requestedInPath);

      // Grab and process the "out" path request.
      String requestedOutPath = argmap.get("out");
      outPath = Paths.get(requestedOutPath);

      // Verify that the I/O directories can be located on the disk.
      if(! inPath.toFile().isDirectory()) {
        System.out.println("> Unable to resolve the input path \""
                            + inPath.toString() + "\".");
        System.exit(1);
      }

      if(! outPath.toFile().isDirectory()) {
        System.out.println("> Unable to resolve the output path \""
                            + outPath.toString() + "\".");
        System.exit(1);
      }

    } catch(InvalidPathException exp) {

      // The user-suggested path was invalid.
      System.out.println("> Unable to resolve the requested I/O paths.");
      System.exit(1);

    }

    // Create a timestamped subfolder in the output directory.
    String timestamp = new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss")
        .format(new Date());
    outPath = outPath.resolve(Paths.get(timestamp));
    if(!outPath.toFile().mkdir()) {
      System.out.println("> Unable to create run directory in output path.");
      System.exit(1);
      return;
    }

    // Write alpha, beta, iter, and num topics.
    PrintWriter metaWriter;
    try {
      File metaFile = outPath.resolve(Paths.get("meta.txt")).toFile();
      metaWriter = new PrintWriter(new FileWriter(metaFile));
    } catch(IOException e) {
      System.out.println("Unable to get a lock on output file.");
      System.exit(1);
      return;
    }

    // Print the meta information.
    System.out.println("> Printing run meta information.");
    metaWriter.println(alphaSum);
    metaWriter.println(beta);
    metaWriter.println(numIterations);
    metaWriter.println(numTopics);
    metaWriter.flush();
    metaWriter.close(); // Close the active resource.

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
    pipeList.add(new Input2CharSequence("UTF-8"));
    pipeList.add(new CharSequence2TokenSequence(
                          Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")));
    pipeList.add(new TokenSequenceLowercase());
    //pipeList.add(new TokenSequenceRemoveStopwords(false, false));
    pipeList.add(new TokenSequence2FeatureSequence());
    return new SerialPipes(pipeList);

  }


  /**
   * Given a list of directories, read in their contents and generate a
   * FileIterator over them (recurses into child directories).
   *
   * @param directories list of file pointers to data directories (per set)
   * @return iterator over data files
   */
  private static FileIterator getDataIterator(File[] directories) {

    // Construct a file iterator recursing over the data directories that
    // only accepts files with the .txt extension.
    FileIterator iterator =
      new FileIterator(directories,
                        new FileFilter() {
                          @Override
                          public boolean accept(File file) {
                            return file.toString().endsWith(".txt") &&
                                   file.isFile();
                          }
                        },
                        FileIterator.LAST_DIRECTORY);

    return iterator;

  }


  /**
   * Create an untrained LDA Topic Model with the instance data.
   *
   * @param instances set of data instances
   * @return untrained LDA topic model
   */
  private static ParallelTopicModel buildModel(InstanceList instances) {

    // Create the topic model.
    // 1st paremeter: number of topics
    // 2nd parameter: alpha sum, defaults to number of topics
    // 3rd parameter: beta, defaults to 0.01
    ParallelTopicModel model = new ParallelTopicModel(
        numTopics, alphaSum, beta);

    // Set data instances.
    model.addInstances(instances);

    // Use two parallel samplers, which each look at one half the corpus and combine
    // statistics after every iteration.
    model.setNumThreads(numThreads);

    // Run the model for n iterations and stop.
    // For debugging, n=50 is a good number.
    // For real applications, use n=1000 to n=2000 iterations.
    model.setNumIterations(numIterations);

    return model;

  }


  /**
   * Format and output the results of an LDA computation.
   *
   * @param model The parallel LDA model to read from.
   */
  private static void printResults(ParallelTopicModel model) {

    // Define a PrintWriter for the document and topic CSV files.
    PrintWriter documentWriter, topicWriter;
    try {
      File documentFile = outPath.resolve(Paths.get("documents.csv")).toFile();
      File topicFile = outPath.resolve(Paths.get("topics.csv")).toFile();
      documentWriter = new PrintWriter(new FileWriter(documentFile));
      topicWriter = new PrintWriter(new FileWriter(topicFile));
    } catch(IOException e) {
      System.out.println("Unable to get a lock on output files.");
      System.exit(1);
      return;
    }

    System.out.println("> Printing document key.");

    // Print the CSV header.
    documentWriter.println("docid,courseid,topic...");

    ArrayList<TopicAssignment> data = model.getData();
    for(int document = 0; document < data.size(); document++) {

      // Isolate the course ID (the filename minus the .txt extension).
      Object name = data.get(document).instance.getName();
      Path filepath = Paths.get((URI)name);
      String filename = filepath.getFileName().toString();
      String course = filename.substring(0, filename.lastIndexOf('.'));
      documentWriter.printf("%d,%s", document, course);

      // Get the proportion values for this instance.
      double[] topicProbabilities = model.getTopicProbabilities(document);

      for(int topic = 0; topic < topicProbabilities.length; topic++) {
        double proportion = topicProbabilities[topic];
        documentWriter.printf(",%d:%f", topic, proportion);
      }

      documentWriter.println();
    }
    documentWriter.flush();
    documentWriter.close(); // Close the active resource.

    System.out.println("> Printing topic key.");

    topicWriter.print("topicid");
    for(int i = 0; i < numWords; i++)
      topicWriter.print(",word");
    topicWriter.println();

    Object[][] topics = model.getTopWords(numWords);
    for(int i = 0; i < topics.length; i++) {
      Object[] topic = topics[i]; // Get topic's word list.
      topicWriter.printf("%d", i);
      for(int j = 0; j < topic.length; j++) {
        String word = topic[j].toString();
        topicWriter.printf(",%s", word);
      }
      topicWriter.println();
    }
    topicWriter.flush();
    topicWriter.close(); // Close the active resource.
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
    model.printDocumentTopics(new PrintWriter(System.out), 0.0, 5);



  }
}}} */


}
