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
from threading import Lock

import utils

logger = logging.getLogger(__name__)

port: int = 5678
socket: zmq.Socket
finished: bool = False
lock = Lock()


def setup_zmq() -> None:
    global socket
    global port
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:%s" % port)


def send_message(topic: str, payload: str) -> None:
    global socket
    lock.acquire()
    socket.send_multipart([bytes(topic, "UTF-8"), bytes(payload, "UTF-8")])
    lock.release()


def fast_forward_to_next_event_start(input_stream: Any) -> (str, str, int, bool):
    while not finished:
        line = bytes(input_stream.readline(timeout=1)).decode('UTF-8').strip()
        matching = re.match("(.*): {", line)
        if matching is None:
            continue
        event_type = matching.group(1)
        return event_type, "{", line.count('{') - line.count('}'), False
    return "", "", 0, True


def handle_progress_event(event: dict, event_type: str) -> None:
    # Add timestamp and forward message to downstream
    event["timestamp"] = datetime.now()
    event["type"] = event_type

    # logging.info(f"[{event_type}] {json.dumps(event, sort_keys=True, default=str)}")
    send_message("progress", json.dumps(event, default=str))


def handle_progress_stream(stream: Any) -> None:
    global finished
    event_type, acc, balance, end_of_stream = fast_forward_to_next_event_start(stream)

    while True:
        line = bytes(stream.readline(timeout=1)).decode('UTF-8').strip()
        if len(line) > 0:
            acc += line
            balance = balance + line.count('{') - line.count('}')
        else:
            if finished:
                break

        try:
            if balance == 0:
                o = json.loads(acc)
                handle_progress_event(o, event_type)

                event_type, acc, balance, end_of_stream = fast_forward_to_next_event_start(stream)
        except JSONDecodeError:
            pass

    logger.info("Progress stream closed")


def handle_console_event(line: str) -> None:
    console_event = {
        "timestamp": datetime.now(),
        "data": line
    }

    send_message("console", json.dumps(console_event, default=str))


def handle_console_stream(stream: Any) -> None:
    global finished
    in_json_job = False
    acc = ""
    balance: int = 0

    while True:
        line = bytes(stream.readline(timeout=1)).decode('UTF-8').strip()
        if len(line) > 0:
            handle_console_event(line)

            # TODO Move the JSON job description in the Java dashboard verticle, and expose it with websocket & REST endpoint
            if in_json_job:
                acc += line
                balance = balance + line.count('{') - line.count('}')
                try:
                    if balance == 0:
                        job = json.loads(acc)
                        in_json_job = False
                        # TODO How to expose it to HandBrake-progress-renderer?
                        logger.info(f"Job description detected: {job}")
                except JSONDecodeError:
                    pass
            if line.endswith("json job:"):
                in_json_job = True
        else:
            if finished:
                break

    logger.info("Console stream closed")


def wrap_handbrake_process(configuration: dict) -> None:
    global finished
    command_line = f"'{configuration.get('handbrake_cli_path')}' --json" \
                   f" --inline-parameter-sets --subtitle-lang-list fre --all-subtitles" \
                   f" --preset-import-file '{configuration.get('preset_file')}'" \
                   f" --preset '{configuration.get('preset')}'" \
                   f" -i '{configuration.get('input_file')}'" \
                   f" -o '{configuration.get('output_file')}'"
    logging.debug(f"command line: <{command_line}>")

    capture_progress = Capture()
    thread_progress = threading.Thread(target=handle_progress_stream, args=(capture_progress,), name="t/out/progress")
    thread_progress.start()

    capture_console = Capture()
    thread_console = threading.Thread(target=handle_console_stream, args=(capture_console,), name="t/err/console")
    thread_console.start()

    pipeline = run(command_line, stdout=capture_progress, stderr=capture_console)
    return_code = pipeline.commands[0].poll()
    while return_code is None:
        return_code = pipeline.commands[0].poll()
        time.sleep(1)

    finished = True

    thread_progress.join()
    thread_console.join()

    # Don't close the 2 capture's, otherwise this will end the streams remainder abruptly.
    # Seems strange, though.

    # That's all folks!


def main(argv: [str]) -> None:
    # TODO Validate settings
    # ? https://docs.python.org/3.6/howto/argparse.html
    wrap_handbrake_process({  # TODO Externalized settings
        'handbrake_cli_path': "/Users/dimitri/Applications/HandBrake/1.3.1/HandBrakeCLI",
        'settings': "--inline-parameter-sets --subtitle-lang-list fre --all-subtitles",
        'preset_file': f"/Users/dimitri/Applications/HandBrake/presets/Capture VooCorder.json",
        'preset': "Capture VooCorder",
        'input_file': "/Users/dimitri/Applications/HandBrake/_1-inbox/sample.mkv",
        'output_file': "/Users/dimitri/Applications/HandBrake/_2-done/sample.mp4"
    })


if __name__ == '__main__':
    utils.setup_logging()
    setup_zmq()
    main(sys.argv)
