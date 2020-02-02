import yaml
import logging
import logging.config


def setup_logging(path: str = "../resources/logging.yaml") -> None:
    with open(path, "r") as file:  # FIXME Relative path
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)
