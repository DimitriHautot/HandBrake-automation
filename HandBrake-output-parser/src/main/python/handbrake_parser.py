#!/user/bin/env python3

# Inspired by https://stackoverflow.com/a/49178529/967410

import json
import logging
import logging.config
import re
import sys
import threading
import time
from datetime import datetime
from json import JSONDecodeError
from typing import Any

import zmq
from sarge import run, Capture

import utils

logger = logging.getLogger(__name__)

port: int = 5678
socket: zmq.Socket
finished: bool = False


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


def send_message(topic: str, payload: str) -> None:
    socket.send_multipart([bytes(topic, "UTF-8"), bytes(payload, "UTF-8")])


def fast_forward_to_next_event_start(input_stream: Any) -> (str, str, int, bool):
    while not finished:
        line = bytes(input_stream.readline(timeout=1)).decode('UTF-8').strip()
        matching = re.match("(.*): {", line)
        if matching is None:
            continue
        event_type = matching.group(1)
        return event_type, "{", line.count('{') - line.count('}'), False
    return "", "", 0, True


def handle_events_stream(stream: Any) -> None:
    event_type, acc, balance, end_of_stream = fast_forward_to_next_event_start(stream)

    while not finished:
        line = bytes(stream.readline(timeout=1)).decode('UTF-8').strip()
        if line != "":
            acc += line
            balance = balance + line.count('{') - line.count('}')

        try:
            if balance == 0:
                o = json.loads(acc)
                handle_event(o, event_type)

                event_type, acc, balance, end_of_stream = fast_forward_to_next_event_start(stream)
        except JSONDecodeError:
            pass
    logger.info("Events stream closed")


def handle_information_stream(stream: Any) -> None:
    while not finished:
        line = stream.readline(timeout=1).strip()
        if len(line) > 0:
            logging.info(f"info: {bytes(line).decode('UTF-8')}")  # TODO Gather information
    logger.info("Information stream closed")


def wrap_handbrake_process(configuration: dict) -> None:
    global finished
    command_line = f"'{configuration.get('handbrake_cli_path')}' --json" \
                   f" --inline-parameter-sets --subtitle-lang-list fre --all-subtitles" \
                   f" --preset-import-file '{configuration.get('preset_file')}'" \
                   f" --preset '{configuration.get('preset')}'" \
                   f" -i '{configuration.get('input_file')}'" \
                   f" -o '{configuration.get('output_file')}'"
    logging.debug(f"command line: <{command_line}>")

    capture_events = Capture()
    thread_events = threading.Thread(target=handle_events_stream, args=(capture_events,), name="t/out/events")
    thread_events.start()

    capture_infos = Capture()
    thread_infos = threading.Thread(target=handle_information_stream, args=(capture_infos,), name="t/err/infos")
    thread_infos.start()

    pipeline = run(command_line, stdout=capture_events, stderr=capture_infos)
    return_code = pipeline.commands[0].poll()
    while return_code is None:
        return_code = pipeline.commands[0].poll()
        time.sleep(1)

    finished = True
    capture_events.close(True)
    capture_infos.close(True)

    # That's all folks!


def main(argv: [str]) -> None:
    if len(argv) == 1:
        handle_events_stream(sys.stdin)
    else:
        # TODO Validate settings
        # ? https://docs.python.org/3.6/howto/argparse.html
        wrap_handbrake_process({  # TODO Externalized settings
            'handbrake_cli_path': "/Users/dimitri/Applications/HandBrake/1.3.1/HandBrakeCLI",
            'settings': "--inline-parameter-sets --subtitle-lang-list fre --all-subtitles",
            'preset_file': f"/Users/dimitri/Applications/HandBrake/presets/Capture VooCorder.json",
            'preset': "Capture VooCorder",
            'input_file': "/Users/dimitri/Applications/HandBrake/_1-inbox/sample.mkv",
            'output_file': "/Users/dimitri/Applications/HandBrake/_2-done/sample.mp4"
            # 'input_file': "/Users/dimitri/Applications/HandBrake/_1-inbox/2019-08-13-10h12m29s241.mov",
            # 'output_file': "/Users/dimitri/Applications/HandBrake/_2-done/2019-08-13-10h12m29s241.mp4"
        })


if __name__ == '__main__':
    utils.setup_logging()
    setup_zmq()
    main(sys.argv)
