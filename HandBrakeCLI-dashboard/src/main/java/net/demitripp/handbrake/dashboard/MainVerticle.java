package net.demitripp.handbrake.dashboard;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Launcher;
import io.vertx.core.Promise;
import io.vertx.core.http.HttpServer;
import io.vertx.ext.bridge.PermittedOptions;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.handler.StaticHandler;
import io.vertx.ext.web.handler.sockjs.BridgeOptions;
import io.vertx.ext.web.handler.sockjs.SockJSHandler;
import io.vertx.ext.web.handler.sockjs.SockJSHandlerOptions;
import org.zeromq.ZMQ;

public class MainVerticle extends AbstractVerticle {

  public static void main(final String[] args) {
    Launcher.executeCommand("run", MainVerticle.class.getName());
  }

  @Override
  public void start(Promise<Void> startPromise) {
    // TODO build this dynamically
    Configuration configuration = new Configuration("tcp://localhost:5678", 5,
      true, true, 8888);

    final ZMQ.Context context = ZMQ.context(1);
    vertx.deployVerticle(new ProgressEventSubscriberVerticle(configuration, context));
    vertx.deployVerticle(new ConsoleEventSubscriberVerticle(configuration, context));
//    vertx.deployVerticle(new ProgressRendererSpyVerticle());

    Router router = Router.router(vertx);

    SockJSHandlerOptions sockJSHandlerOptions = new SockJSHandlerOptions().setHeartbeatInterval(2_000);
    SockJSHandler sockJSHandler = SockJSHandler.create(vertx, sockJSHandlerOptions);
    PermittedOptions outboundPermitted1 = new PermittedOptions().setAddress("progress.update");
    BridgeOptions bridgeOptions = new BridgeOptions().addOutboundPermitted(outboundPermitted1);
    sockJSHandler.bridge(bridgeOptions);

    router.route("/event-bus/*").handler(sockJSHandler);

    StaticHandler staticHandler = StaticHandler.create()
      .setFilesReadOnly(false)  // TODO Conditional to development mode?
      .setCachingEnabled(false)
      ;
    router.route("/static/*").handler(staticHandler);
    router.route("/*").handler(staticHandler);

    HttpServer server = vertx.createHttpServer();

    server.requestHandler(router).listen(configuration.getWebServerPort());
    startPromise.complete();
  }
}
