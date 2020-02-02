package net.demitripp.handbrake.hpr;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Promise;

/**
 * @author Dimitri Hautot
 */
public class ProgressRendererSpyVerticle extends AbstractVerticle {

  @Override
  public void start(Promise<Void> startPromise) {
    vertx.eventBus().consumer("encoding.update", message -> {
      System.out.println(" received message: " + message.body());
    });

    startPromise.complete();
  }
}
