#!/user/bin/env python3

# Inspired by https://stackoverflow.com/a/49178529/967410

import sys
import json
from json import JSONDecodeError
from typing import Any

import yaml
import logging
import logging.config

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    with open("../resources/logging.yaml", "r") as file:  # FIXME Relative path
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)


def handle_event(event: dict, event_type: str) -> None:
    logging.info(f"[{event_type}] {json.dumps(event, sort_keys=True, default=str)}")
    # TODO Add timestamp and forward message to downstream (0MQ?)


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
    setup_logging()
    main(sys.argv)
