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

    if len(argv) < 2:
        print("Required arguments missing: <topic-name>", file=sys.stderr)
        sys.exit(1)
    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, argv[1])
    socket.connect("tcp://127.0.0.1:5678")


def main(argv: [str]) -> None:
    while True:
        frames = socket.recv_multipart()
        frames = [bytes(frame).decode("UTF-8") for frame in frames]
        if len(frames) > 2:
            logging.warning(frames)
        else:
            logging.info(f"{frames[0]} {frames[1]}")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    utils.setup_logging("../../main/resources/logging.yaml")
    init_zmq(sys.argv)
    main(sys.argv)
