#!/user/bin/env python3

# Inspired by https://stackoverflow.com/a/49178529/967410

import sys
import zmq
import json
from json import JSONDecodeError
from typing import Any

import logging
import logging.config
from datetime import datetime
import utils

logger = logging.getLogger(__name__)

port: int = 5678
socket: zmq.Socket


def setup_zmq() -> None:
    global socket
    global port
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:%s" % port)


def handle_event(event: dict, event_type: str) -> None:
    logging.info(f"[{event_type}] {json.dumps(event, sort_keys=True, default=str)}")
    # Add timestamp and forward message to downstream
    event["timestamp"] = datetime.now()
    event["type"] = event_type

    send_message("foo", json.dumps(event, default=str))


def send_message(topic: str, payload: str):
    # message: str = payload
    # if topic is not None and len(topic) > 0:
    #     message = f"{topic} {payload}"
    # socket.send_string(message)
    socket.send_multipart([bytes(topic, "UTF-8"), bytes(payload, "UTF-8")])


# TODO Use more generic regex instead of string comparisons
def forward_to_event_start(input_stream: Any) -> (str, str, int, bool):
    while True:
        line = input_stream.readline().strip()
        if line != "Version: {" and line != "Progress: {":
            continue
        else:
            if line == "Version: {":
                return "Version", "{", line.count('{') - line.count('}'), False
            if line == "Progress: {":
                return "Progress", "{", line.count('{') - line.count('}'), False
            return "Unknown", "{", line.count('{') - line.count('}'), False


def main(argv: [str]) -> None:
    input_stream = sys.stdin
    event_type, acc, balance, end_of_stream = forward_to_event_start(input_stream)

    while not end_of_stream:
        line = input_stream.readline().strip()
        if line != "":
            acc += line
            balance = balance + line.count('{') - line.count('}')

        try:
            if balance == 0:
                o = json.loads(acc)
                handle_event(o, event_type)

                event_type, acc, balance, end_of_stream = forward_to_event_start(input_stream)
        except JSONDecodeError:
            pass


if __name__ == '__main__':
    utils.setup_logging()
    setup_zmq()
    main(sys.argv)
