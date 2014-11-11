package edu.gmu.jrouly.trajectory;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import java.io.File;
import java.io.Reader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.FileInputStream;
import java.io.FileFilter;

import java.nio.file.InvalidPathException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.util.ArrayList;
import java.util.Formatter;
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
import cc.mallet.topics.TopicInferencer;

import cc.mallet.types.Alphabet;
import cc.mallet.types.FeatureSequence;
import cc.mallet.types.IDSorter;
import cc.mallet.types.LabelSequence;
import cc.mallet.types.InstanceList;
import cc.mallet.types.Instance;

/**
 * The main executable class of the trajectory project to perform topic
 * modeling.
 */
public class Trajectory {

  static Pipe pipe;

  /**
   * Perform topic modeling on the data set as constrained by any command
   * line arguments.
   *
   * @param args command line specifications
   */
  public static void main(String[] args) {

    // Allow debugging output to show.
    Option debugOption = new Option( "debug", "print debug messages" );

    // Specify the data directory to read from.
    Option dataDirOption = OptionBuilder.withArgName("path")
                                  .hasArg()
                                  .withDescription( "path to the data directory" )
                                  .create("data");
    dataDirOption.setRequired( true );

    // Add options to the options dictionary.
    Options options = new Options();
    options.addOption( debugOption );
    options.addOption( dataDirOption );

    // Create an argument parser.
    CommandLineParser parser = new BasicParser();

    // Create argument value holders.
    Path dataDirPath = Paths.get( "data" );
    boolean debug = false;

    try {

      // Parse the command line arguments.
      CommandLine line = parser.parse( options, args );

      if( line.hasOption( "data" ) ) {
        String requestedDataDir = line.getOptionValue( "data" );
        dataDirPath = Paths.get( requestedDataDir );
      }

      debug = line.hasOption( "debug" );

    } catch( ParseException exp ) {

      // Something went wrong!
      System.err.println( "Parsing failed. Reason: " + exp.getMessage() );
      System.err.println();
      HelpFormatter formatter = new HelpFormatter();
      formatter.printHelp( "trajectory", options );
      System.exit( 1 );

    } catch( InvalidPathException exp ) {

      // The user-suggested path was invalid.
      System.err.println( "Unable to find the resolve data path." );
      System.exit( 1 );

    }

    if( debug ) System.out.println( "dataDirPath: " + dataDirPath.toString() );



    // Generate data processing pipeline.
    pipe = buildPipe();

    // Generate list of data directories.
    File[] dataDirectories = listDataDirectories( dataDirPath );

    // Generate instances from the input data files.
    InstanceList instances = readDirectories( dataDirectories );

    // Create the topic model.
    int numTopics = 100;
    ParallelTopicModel model = new ParallelTopicModel( numTopics, 1.0, 0.01 );
    model.addInstances( instances );

    // Use two parallel samplers, which each look at one half the corpus and combine
    // statistics after every iteration.
    model.setNumThreads(2);

    // Run the model for 50 iterations and stop (this is for testing only,
    //  for real applications, use 1000 to 2000 iterations)
    model.setNumIterations(50);
    try {
      model.estimate();
    } catch( IOException exp ) {
      // The model broke when reading in files.
      System.err.println( "Error estimating topics when reading from data set." );
      System.exit( 1 );
    }



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









  }


  /**
   * Given a path to the root data directory, generate a list of its
   * content directories.
   *
   * @param dataDirPath path to the root data directory
   * @return list of file pointers to content directories
   */
  private static File[] listDataDirectories( Path dataDirPath ) {

    // Generate list of data directories in the data path.
    File dataDirFile = dataDirPath.toFile();
    if( ! dataDirFile.isDirectory() ) {
      System.err.println( "Data directory is not a directory." );
      System.exit( 1 );
    }
    File[] dataDirContents = dataDirFile.listFiles();
    return dataDirContents;

  }


  /**
   * Build a workflow pipe that cleans and tokenizes the input data.
   *
   * @return cleaning pipe
   */
  private static Pipe buildPipe() {

    // Read in English stopwords.
    //InputStream stoplistIn = Trajectory.class.getResourcesAsStream("/stoplists/en.txt");


    // Begin by importing documents from text.
    ArrayList<Pipe> pipeList = new ArrayList<Pipe>();

    // Pipes: lowercase, tokenize, remove stopwords, map to features.
    pipeList.add( new Input2CharSequence("UTF-8") );
    pipeList.add( new CharSequence2TokenSequence(Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")) );
    pipeList.add( new TokenSequenceLowercase() );
    pipeList.add( new TokenSequenceRemoveStopwords(false, false) );
    pipeList.add( new TokenSequence2FeatureSequence() );
    return new SerialPipes(pipeList);

  }


  /**
   * Given a list of directories, read in their contents and generate an
   * InstanceList.
   *
   * @param directories list of file pointers to data directories (per set)
   * @return list of data instances
   */
  private static InstanceList readDirectories( File[] directories ) {

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

    InstanceList instances = new InstanceList( pipe );
    instances.addThruPipe( iterator );

    return instances;

  }

}
