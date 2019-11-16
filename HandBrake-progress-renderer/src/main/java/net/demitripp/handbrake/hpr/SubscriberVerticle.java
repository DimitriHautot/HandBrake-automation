package net.demitripp.handbrake.hpr;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Promise;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * @author Dimitri Hautot
 */
public class SubscriberVerticle extends AbstractVerticle {

  private ExecutorService executor;
  private Subscriber subscriber;

  @Override
  public void start() {
    subscriber = new Subscriber("tcp://localhost:5678", "foo", vertx);
    executor = Executors.newFixedThreadPool(2, r -> {
      Thread thread = new Thread(r);
      thread.setUncaughtExceptionHandler((t, e) -> e.printStackTrace());
      return thread;
    });
    executor.submit(subscriber);
  }

  @Override
  public void stop(Promise<Void> stopPromise) throws Exception {
    subscriber.stop();

    executor.shutdown();
    executor.awaitTermination(30, TimeUnit.SECONDS);

    stopPromise.complete();
  }
}
