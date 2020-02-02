#!/user/bin/env python3

# Inspired byt https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pubsub.html

import sys
import zmq
import logging.config
import utils
import signal


def signal_handler(sig, frame):
    sys.exit(0)


logger = logging.getLogger(__name__)
signal.signal(signal.SIGINT, signal_handler)
utils.setup_logging("../../main/resources/logging.yaml")

# Socket to talk to server
port_console = 5679
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE, "console")
socket.connect("tcp://127.0.0.1:%s" % port_console)

while True:
    topic, console_event = socket.recv_multipart()
    msg = bytes(console_event).decode("UTF-8")
    logging.info(msg)

    # array = socket.recv_multipart()
    # msg = bytes(array[1]).decode("UTF-8")
    # logging.info(msg)
    # if len(array) > 2:
    #     logger.info(f"Array size: {len(array)}")
    #     logger.info(f"Array: {array}")
