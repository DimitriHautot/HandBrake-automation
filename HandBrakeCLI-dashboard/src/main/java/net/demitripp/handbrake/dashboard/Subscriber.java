package net.demitripp.handbrake.dashboard;

import io.vertx.core.Vertx;
import org.zeromq.SocketType;
import org.zeromq.ZMQ;

import java.util.Arrays;

/**
 * @author Dimitri Hautot
 */
public class Subscriber implements Runnable {

  private final ZMQ.Context context;
  private final String address;
  private final String topic;
  private final byte[] topicBytes;
  private final String eventType;
  private final Vertx vertx;
  private final boolean verbose;
  private ZMQ.Socket subscriber;
  private volatile boolean stop = false;

  Subscriber(ZMQ.Context context, String address, String topic, String eventType, Vertx vertx, boolean verbose) {
    this.context = context;
    this.address = address;
    this.topic = topic;
    this.topicBytes = topic.getBytes();
    this.eventType = eventType;
    this.vertx = vertx;
    this.verbose = verbose;
  }

  @Override
  public void run() {
    subscriber = context.socket(SocketType.SUB);
    subscriber.setLinger(0);
    subscriber.connect(address);
    subscriber.subscribe(topic);

    while (! stop) {
      byte[] recv = subscriber.recv();
      if (Arrays.compare(topicBytes, recv) == 0) {
        continue;
      }
      String message = new String(recv);
      if (verbose) {
        System.out.println(String.format("[%s] Received message: %s", topic, message));
      }
      vertx.eventBus().publish(eventType, message);
    }

    cleanup();
  }

  void stop() {
    stop = true;
  }

  private void cleanup() {
    subscriber.unsubscribe(topic);
    subscriber.disconnect(address);
    subscriber.close();
    context.close();
  }
}
