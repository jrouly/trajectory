package edu.gmu.jrouly.trajectory;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

/**
 * A custom Apache CLI command line argument parser for Trajectory.
 */
public class CLIParser {

  /**
   * Generates an ApacheCLI Options object with Debug and Data Directory
   * parameters.
   *
   * @return configured command line options
   */
  private static Options getOptions() {

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

    return options;

  }

}
