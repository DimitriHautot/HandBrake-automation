#!/user/bin/env python3

# Inspired byt https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html

import sys
import zmq
import logging.config
import utils
import signal

port: int
socket: zmq.Socket


def signal_handler(sig, frame):
    sys.exit(0)


def init_zmq(argv: [str]) -> None:
    global port
    global socket

    if len(argv) < 3:
        print("Required arguments missing: <topic-name> <host:port>", file=sys.stderr)
        sys.exit(1)
    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, argv[1])
    socket.connect(f"tcp://{argv[2]}")


def main(argv: [str]) -> None:
    while True:
        topic, event = socket.recv_multipart()
        msg = bytes(event).decode("UTF-8")
        logging.info(msg)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    utils.setup_logging("../../main/resources/logging.yaml")
    init_zmq(sys.argv)
    main(sys.argv)
