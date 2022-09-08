import argparse
import json
import os
import logging
import logging.config
import logging.handlers
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
        "-D",
        "--debug",
        action="store_true",
        help="log debug messages to stderr",
    )
    parser.add_argument(
        "-L",
        "--level",
        type=log_level,
        default=logging.WARNING,
        metavar="DEBUG, INFO, WARNING, ERROR (default WARNING)",
        help="the logging level",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=argparse.FileType("r"),
        help="configuration dictionary schema describing logging configuration in json or yaml",
    )
    parser.add_argument(
        "--allow-reuse-address",
        dest="allow_reuse_address",
        action="store_true",
        help="allow socket to reuse address",
    )
    parser.add_argument(
        "--logger-name",
        dest="logger_name",
        default="logdriver",
        help="the name of the logger",
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    system_logger = logging.getLogger("logdriver.system")
    system_handler = logging.StreamHandler(stream=sys.stderr)
    system_logger.addHandler(system_handler)
    if args.debug:
        system_logger.setLevel(logging.DEBUG)

    system_logger.warning("Started logdriver logging socket server")
    system_logger.debug("Debug is ON")
    system_logger.warning(f"Listening for logs on {args.host}:{args.port}")
    system_logger.warning("Press CTRL+C to quit")

    if args.file:
        logging.config.dictConfig(json.loads(args.file.read()))
        system_logger.debug(f"Using dictionary config {args.file.name}")
        user_logger = logging.getLogger(args.logger_name)
    else:
        user_logger = logging.getLogger(args.logger_name)
        user_handler = logging.StreamHandler(stream=sys.stdout)
        user_handler.setLevel(args.level)
        user_logger.addHandler(user_handler)

    logdriver.server.main(
        args.host, args.port, system_logger, user_logger, args.allow_reuse_address
    )

    system_logger.warning("Bye!")
