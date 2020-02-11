package net.demitripp.handbrake.dashboard;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Promise;
import org.zeromq.ZMQ;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * @author Dimitri Hautot
 */
public class ProgressEventSubscriberVerticle extends AbstractVerticle {

  private ExecutorService executor;
  private Subscriber subscriber;
  private final Configuration configuration;
  private final ZMQ.Context context;

  public ProgressEventSubscriberVerticle(Configuration configuration, ZMQ.Context context) {
    this.configuration = configuration;
    this.context = context;
  }

  @Override
  public void start() {
    subscriber = new Subscriber(this.context, configuration.getZmqEndpoint(), "progress", "progress.update", vertx, configuration.isProgressEventsVerbose());
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
    executor.awaitTermination(configuration.getTerminationTimeoutSeconds(), TimeUnit.SECONDS);

    stopPromise.complete();
  }
}
