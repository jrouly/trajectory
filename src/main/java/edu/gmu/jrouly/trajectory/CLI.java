package edu.gmu.jrouly.trajectory;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import java.util.HashMap;
import java.util.Map;

/**
 * A custom Apache CLI command line argument parser for Trajectory.
 */
public class CLI {


  /**
   * Generates an ApacheCLI Options object with Debug and Data Directory
   * parameters.
   *
   * @return configured command line options
   */
  private static Options getOptions() {

    // Allow debugging output to show.
    Option debugOption   = new Option( "debug", "print debug messages" );

    // Specify the number of parallel LDA threads to use in the parallle
    // Mallet model.
    Option threadsOption = OptionBuilder.withArgName("num threads")
                                  .hasArg()
                                  .withDescription( "number of parallel LDA threads" )
                                  .create("threads");

    // Number of iterations when training the LDA model.
    Option iterOption    = OptionBuilder.withArgName("num iterations")
                                  .hasArg()
                                  .withDescription( "number of iterations" )
                                  .create("iterations");

    // Specify the data directory to read from.
    Option dataDirOption = OptionBuilder.withArgName("path")
                                  .hasArg()
                                  .withDescription( "path to the data directory" )
                                  .create("data");
    dataDirOption.setRequired( true );

    // Add options to the options dictionary.
    Options options = new Options();
    options.addOption( debugOption   );
    options.addOption( threadsOption );
    options.addOption( iterOption    );
    options.addOption( dataDirOption );

    return options;

  }


  /**
   * Parse command line arguments and return a map of arguments to values.
   * If an argument doesn't take a value, its value will be null.
   *
   * @param args string array of command line args
   * @return map of arguments and values, if any.
   */
  public static Map<String, String> parse(String[] args) {

    // Initialize variables.
    CommandLineParser parser = new BasicParser();
    Options options = getOptions();
    Map<String, String> map = new HashMap<String, String>();

    try {

      // Parse the command line arguments.
      CommandLine line = parser.parse( options, args );

      // Read the list of parsed, recognized options.
      Option[] parsedOptions = line.getOptions();

      // For each parsed option, store it and its value in a map.
      for( Option o : parsedOptions ) {
        String k = o.getOpt();
        String v = line.getOptionValue( k );
        map.put( k, v );
      }

    } catch( ParseException exp ) {

      // Something went wrong!
      System.err.println( "Parsing failed. Reason: " + exp.getMessage() );
      System.err.println();
      HelpFormatter formatter = new HelpFormatter();
      formatter.printHelp( "trajectory", options );
      System.exit( 1 );

    }

    // Return the new commandline object with parsed values.
    return map;

  }


}
