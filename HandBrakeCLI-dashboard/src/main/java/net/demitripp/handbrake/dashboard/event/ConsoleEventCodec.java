package net.demitripp.handbrake.dashboard.event;

import io.vertx.core.buffer.Buffer;
import io.vertx.core.eventbus.MessageCodec;
import io.vertx.core.json.JsonObject;

import java.time.Instant;

/**
 * @author Dimitri Hautot
 * @see <a href="https://github.com/vert-x3/vertx-examples/blob/master/core-examples/src/main/java/io/vertx/example/core/eventbus/messagecodec/util/CustomMessageCodec.java">This class</a>
 */
public class ConsoleEventCodec implements MessageCodec<ConsoleEvent, ConsoleEvent> {

  @Override
  public void encodeToWire(Buffer buffer, ConsoleEvent consoleEvent) {
    JsonObject jsonToEncode = new JsonObject();
    jsonToEncode.put("timestamp", consoleEvent.getTimestamp());
    jsonToEncode.put("data", consoleEvent.getData());

    String jsonString = jsonToEncode.encode();
    int length = jsonString.getBytes().length;

    buffer.appendInt(length);
    buffer.appendString(jsonString);
  }

  @Override
  public ConsoleEvent decodeFromWire(int position, Buffer buffer) {
    int _pos = position;
    int length = buffer.getInt(_pos);
    String jsonString = buffer.getString(_pos += 4, _pos += length);
    JsonObject json = new JsonObject(jsonString);
    Instant timestamp = json.getInstant("timestamp");
    String data = json.getString("data");
    return new ConsoleEvent(timestamp, data);
  }

  @Override
  public ConsoleEvent transform(ConsoleEvent consoleEvent) {
    return consoleEvent;
  }

  @Override
  public String name() {
    return this.getClass().getSimpleName();
  }

  @Override
  public byte systemCodecID() {
    return -1;
  }
}
