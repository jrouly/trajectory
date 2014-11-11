package edu.gmu.jrouly.trajectory;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import java.nio.file.Paths;

import java.io.File;

import java.util.ArrayList;
import java.util.regex.Pattern;

import cc.mallet.pipe.CharSequenceLowercase;
import cc.mallet.pipe.CharSequence2TokenSequence;
import cc.mallet.pipe.Pipe;
import cc.mallet.pipe.TokenSequenceRemoveStopwords;
import cc.mallet.pipe.TokenSequence2FeatureSequence;

/**
 * The main executable class of the trajectory project to perform topic
 * modeling.
 */
public class Trajectory {

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

  }
}
