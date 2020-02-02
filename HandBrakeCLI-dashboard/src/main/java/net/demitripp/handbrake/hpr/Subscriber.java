package net.demitripp.handbrake.hpr;

import io.vertx.core.Vertx;
import org.zeromq.SocketType;
import org.zeromq.ZMQ;

import java.util.Arrays;

/**
 * @author Dimitri Hautot
 */
public class Subscriber implements Runnable {

  private final ZMQ.Context context = ZMQ.context(1);
  private final String address;
  private final String topic;
  private final byte[] topicBytes;
  private Vertx vertx;
  private ZMQ.Socket subscriber;
  private volatile boolean stop = false;

  Subscriber(String address, String topic, Vertx vertx) {
    this.address = address;
    this.topic = topic;
    this.topicBytes = topic.getBytes();
    this.vertx = vertx;
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
      System.out.println("Received message " + message);
      vertx.eventBus().publish("encoding.update", message);
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
