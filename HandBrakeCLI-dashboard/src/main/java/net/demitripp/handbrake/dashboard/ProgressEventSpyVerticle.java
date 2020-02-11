package net.demitripp.handbrake.dashboard;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Promise;

/**
 * @author Dimitri Hautot
 */
public class ProgressEventSpyVerticle extends AbstractVerticle {

  @Override
  public void start(Promise<Void> startPromise) {
    vertx.eventBus().consumer("progress.update", message -> {
//      System.out.println(" received message: " + message.body());
    });

    startPromise.complete();
  }
}
