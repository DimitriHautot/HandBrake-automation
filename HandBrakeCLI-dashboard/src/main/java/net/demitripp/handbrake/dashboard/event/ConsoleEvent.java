package net.demitripp.handbrake.dashboard.event;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.ToString;

import java.time.Instant;

/**
 * @author Dimitri Hautot
 */
@Getter
@ToString
@RequiredArgsConstructor
public class ConsoleEvent {

  private final Instant timestamp;
  private final String data;

}
