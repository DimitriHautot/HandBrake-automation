package net.demitripp.handbrake.dashboard;

import io.vertx.core.Vertx;
import io.vertx.core.eventbus.Message;
import io.vertx.core.json.DecodeException;
import io.vertx.core.json.JsonObject;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.impl.RouterImpl;
import net.demitripp.handbrake.dashboard.event.ConsoleEvent;

/**
 * @author Dimitri Hautot
 */
public class ApiRouter extends RouterImpl implements Router {

  private Message<Object> latestConsoleEventMessage, latestProgressEventMessage;
  private JsonObject jsonJob;
  private boolean inJsonJob;
  private String accumulator = "";
  private int balance = 0;

  public ApiRouter(Vertx vertx) {
    super(vertx);
    init(vertx);
  }

  private void init(Vertx vertx) {
    vertx.eventBus().consumer("progress.update", message -> latestProgressEventMessage = message);
    vertx.eventBus().consumer("console.update",  message -> {
      latestConsoleEventMessage = message;
      detectJsonJob(message);
    });

    this.get("/current-status").handler(rc -> {
      String result = new JsonObject()
        .put("latestConsoleEvent", latestConsoleEventMessage.body())
        .put("progressConsoleEvent", latestProgressEventMessage.body())
        .put("jsonJob", this.jsonJob)
        .toString();
      rc.response()
        .putHeader("Content-Length", String.valueOf(result.length()))
        .write(result)
        .end();
    });
  }

  private void detectJsonJob(Message<Object> consoleEventMessage) {
    ConsoleEvent consoleEvent = (ConsoleEvent) consoleEventMessage.body();
    if (consoleEvent.getData().endsWith("json job:")) {
      this.inJsonJob = true;
    } else if (this.inJsonJob) {
      this.accumulator += consoleEvent.getData();
      this.balance += consoleEvent.getData().chars().filter(ch -> ch == '{').count()
        - consoleEvent.getData().chars().filter(ch -> ch == '}').count();
      if (this.balance == 0) {
        try {
          this.jsonJob = new JsonObject(this.accumulator);
          this.inJsonJob = false;
        } catch (DecodeException decodeException) {
          // False positive
        }
      }
    }
  }
}
