package net.demitripp.handbrake.hpr;

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

public class MainVerticle extends AbstractVerticle {

  public static void main(final String[] args) {
    Launcher.executeCommand("run", MainVerticle.class.getName());
  }

  @Override
  public void start(Promise<Void> startPromise) {
    vertx.deployVerticle(new SubscriberVerticle());
    vertx.deployVerticle(new ProgressRendererSpyVerticle());

    Router router = Router.router(vertx);

    SockJSHandlerOptions sockJSHandlerOptions = new SockJSHandlerOptions().setHeartbeatInterval(2_000);
    SockJSHandler sockJSHandler = SockJSHandler.create(vertx, sockJSHandlerOptions);
    PermittedOptions outboundPermitted1 = new PermittedOptions().setAddress("encoding.update");
    BridgeOptions bridgeOptions = new BridgeOptions().addOutboundPermitted(outboundPermitted1);
    sockJSHandler.bridge(bridgeOptions);

    router.route("/event-bus/*").handler(sockJSHandler);

    StaticHandler staticHandler = StaticHandler.create();
    router.route("/static/*").handler(staticHandler);
    router.route("/*").handler(staticHandler);

    HttpServer server = vertx.createHttpServer();

//    router.route().handler(routingContext -> {
//
//      // This handler will be called for every request
//      HttpServerResponse response = routingContext.response();
//      response.putHeader("content-type", "text/plain");
//
//      // Write to the response and end it
//      response.end("Hello World from Vert.x-Web!");
//    });

    server.requestHandler(router).listen(80);
    startPromise.complete();
  }
}
