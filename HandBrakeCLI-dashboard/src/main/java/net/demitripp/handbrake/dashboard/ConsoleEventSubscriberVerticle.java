package net.demitripp.handbrake.dashboard;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Promise;
import net.demitripp.handbrake.dashboard.event.ConsoleEvent;
import net.demitripp.handbrake.dashboard.event.ConsoleEventCodec;
import org.zeromq.ZMQ;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * @author Dimitri Hautot
 */
public class ConsoleEventSubscriberVerticle extends AbstractVerticle {

  private ExecutorService executor;
  private Subscriber subscriber;
  private final Configuration configuration;
  private final ZMQ.Context context;

  public ConsoleEventSubscriberVerticle(Configuration configuration, ZMQ.Context context) {
    this.configuration = configuration;
    this.context = context;
  }

  @Override
  public void start() {
    vertx.eventBus().registerDefaultCodec(ConsoleEvent.class, new ConsoleEventCodec());

    subscriber = new Subscriber(this.context, configuration.getZmqEndpoint(), "console", "console.update", vertx, configuration.isConsoleEventsVerbose());
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

    vertx.eventBus().unregisterDefaultCodec(ConsoleEvent.class);
    stopPromise.complete();
  }
}
