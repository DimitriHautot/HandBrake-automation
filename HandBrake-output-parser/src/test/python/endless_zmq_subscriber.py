#!/user/bin/env python3

# Inspired byt https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html

import sys
import zmq
import logging.config
import utils
import signal


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
utils.setup_logging("../../main/resources/logging.yaml")

# Socket to talk to server
port = 5678
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE, "foo")
socket.connect("tcp://127.0.0.1:%s" % port)

while True:
    topic, event = socket.recv_multipart()
    msg = bytes(event).decode("UTF-8")
    logging.info(msg)
