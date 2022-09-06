import argparse
import os
import logging
import sys
from typing import Optional, Sequence

import logdriver.server

DESCRIPTION = """
Run a TCP socker server for receiving and handling pickled Python LogRecord objects
"""
MIN_PORT = 1024
MAX_PORT = 65535
PORT_DEFAULT = os.environ.get("LOGDRIVER_DEFAULT_PORT", 9079)
HOST_DEFAULT = "localhost"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]


def port_range(port: str, min_val=MIN_PORT, max_val=MAX_PORT):
    try:
        p = int(port)
        if min_val <= p <= max_val:
            return p
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(
        f"Port needs to be an integer in the range {min_val}-{max_val}"
    )


def log_level(level_str: str) -> int:
    if level_str == "DEBUG":
        return logging.DEBUG
    if level_str == "INFO":
        return logging.INFO
    if level_str == "WARNING":
        return logging.WARNING
    if level_str == "ERROR":
        return logging.ERROR
    raise argparse.ArgumentTypeError(f"Invalid logging level: {level_str}")


def parse_args(args: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-p",
        "--port",
        type=port_range,
        metavar=f"{MIN_PORT}-{MAX_PORT}",
        help=f"the port to bind the socket server on (default {PORT_DEFAULT})",
        default=PORT_DEFAULT,
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        help=f"the host address the server will listen on (default {HOST_DEFAULT})",
        default=HOST_DEFAULT,
    )
    parser.add_argument(
        "-L",
        "--level",
        type=log_level,
        default=logging.WARNING,
        metavar="DEBUG, INFO, WARNING, ERROR (default WARNING)",
        help="the logging level",
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    system_logger = logging.getLogger("logdriver.system")
    system_handler = logging.StreamHandler(stream=sys.stderr)
    system_logger.addHandler(system_handler)

    system_logger.warning("Started logdriver logging socket server")
    system_logger.warning(f"Listening for logs on {args.host}:{args.port}")
    system_logger.warning("Press CTRL+C to quit")

    user_logger = logging.getLogger("logdriver.user")
    user_handler = logging.StreamHandler(stream=sys.stdout)
    user_logger.addHandler(user_handler)

    logdriver.server.main(args.host, args.port, system_logger, user_logger)

    system_logger.warning("Bye!")
