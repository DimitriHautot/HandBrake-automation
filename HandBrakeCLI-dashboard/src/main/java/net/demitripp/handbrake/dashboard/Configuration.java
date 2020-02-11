package net.demitripp.handbrake.dashboard;

import lombok.Data;
import lombok.RequiredArgsConstructor;

/**
 * @author Dimitri Hautot
 */
@Data
@RequiredArgsConstructor
public class Configuration {

  private final String zmqEndpoint;
  private final int terminationTimeoutSeconds;
  private final boolean progressEventsVerbose, consoleEventsVerbose;
  private final int webServerPort;
}
