#!/user/bin/env python3
import random
import time
import sys
import signal
import utils
import handbrake_wrapper


def signal_handler(sig, frame):
    work_done = {
        "State": "WORKDONE",
        "WorkDone": {
            "Error": 0,
            "SequenceID": 1
        }
    }
    handbrake_wrapper.handle_progress_event(work_done, "Progress")

    sys.exit(0)


def main(argv: [str]) -> None:
    version = {
        "Arch": "x86_64",
        "Name": "HandBrake",
        "Official": True,
        "RepoDate": "2019-11-09 20:44:32",
        "RepoHash": "4672248655ddd687161bacdb539c208abde15c59",
        "System": "Linux",
        "Type": "release",
        "Version": {
            "Major": 1,
            "Minor": 3,
            "Point": 0
        },
        "VersionString": "1.3.0"
    }
    scans = [
        {
            "Scanning": {
                "Preview": 1,
                "PreviewCount": 10,
                "Progress": 0.10000000149011612,
                "SequenceID": 0,
                "Title": 1,
                "TitleCount": 1
            },
            "State": "SCANNING"
        }, {
            "Scanning": {
                "Preview": 3,
                "PreviewCount": 10,
                "Progress": 0.30000001192092896,
                "SequenceID": 0,
                "Title": 1,
                "TitleCount": 1
            },
            "State": "SCANNING"
        }, {
            "Scanning": {
                "Preview": 6,
                "PreviewCount": 10,
                "Progress": 0.60000002384185791,
                "SequenceID": 0,
                "Title": 1,
                "TitleCount": 1
            },
            "State": "SCANNING"
        }, {
            "Scanning": {
                "Preview": 10,
                "PreviewCount": 10,
                "Progress": 1.0,
                "SequenceID": 0,
                "Title": 1,
                "TitleCount": 1
            },
            "State": "SCANNING"
        }]
    working = {
        "State": "WORKING",
        "Working": {
            "ETASeconds": 0,
            "Hours": -1,
            "Minutes": -1,
            "Pass": 1,
            "PassCount": 1,
            "PassID": 0,
            "Paused": 0,
            "Progress": 0.50617283582687378,
            "Rate": 2.0972207082081695e-8,
            "RateAvg": 0.0,
            "Seconds": -1,
            "SequenceID": 1
        }
    }
    workdone = {
        "State": "WORKDONE",
        "WorkDone": {
            "Error": 0,
            "SequenceID": 1
        }
    }

    while True:
        handbrake_wrapper.handle_progress_event(version, "Version")
        time.sleep(1)

        for scan in scans:
            handbrake_wrapper.handle_progress_event(scan, "Progress")
            time.sleep(1)

        for pc in range(1, 100):
            working["Working"]["Progress"] = float(pc % 100) / 100
            working["Working"]["RateAvg"] = float(random.randrange(15, 35) / 100)
            handbrake_wrapper.handle_progress_event(working, "Progress")
            time.sleep(0.25)

        handbrake_wrapper.handle_progress_event(workdone, "Progress")
        time.sleep(3)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    utils.setup_logging("../../main/resources/logging.yaml")
    handbrake_wrapper.setup_zmq()
    main(sys.argv)
