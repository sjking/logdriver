import logging
from typing import List

import pytest
import argparse

from logdriver.cli import parse_args, HOST_DEFAULT, PORT_DEFAULT


def make_namespace(
    port: int = PORT_DEFAULT, host: str = HOST_DEFAULT, level: int = logging.WARNING, debug: bool = False
) -> argparse.Namespace:
    return argparse.Namespace(port=port, host=host, level=level, debug=debug)


def test_parse_default():
    assert parse_args([]) == make_namespace()


@pytest.mark.parametrize(
    "args,namespace",
    [
        (["-p", "1024"], make_namespace(port=1024)),
        (["-p", "5001"], make_namespace(port=5001)),
        (["-p", "65535"], make_namespace(port=65535)),
        (["--port", "1024"], make_namespace(port=1024)),
        (["--port", "5001"], make_namespace(port=5001)),
        (["--port", "65535"], make_namespace(port=65535)),
    ],
)
def test_parse_port(args: List[str], namespace: argparse.Namespace):
    assert parse_args(args) == namespace


@pytest.mark.parametrize(
    "args,error_message",
    [
        (["-p", "80"], "Port needs to be an integer in the range 1024-65535"),
        (["-p", "1023"], "Port needs to be an integer in the range 1024-65535"),
        (["-p", "65536"], "Port needs to be an integer in the range 1024-65535"),
        (["-p"], "expected one argument"),
        (["--port", "80"], "Port needs to be an integer in the range 1024-65535"),
        (["--port", "1023"], "Port needs to be an integer in the range 1024-65535"),
        (["--port", "65536"], "Port needs to be an integer in the range 1024-65535"),
        (["--port"], "expected one argument"),
    ],
)
def test_parse_port_error(capsys, args: List[str], error_message: str):
    with pytest.raises(SystemExit):
        parse_args(args)
    captured = capsys.readouterr()
    assert error_message in captured.err


@pytest.mark.parametrize(
    "args,namespace",
    [
        (["-H", "example.localdomain"], make_namespace(host="example.localdomain")),
        (["--host", "example.localdomain"], make_namespace(host="example.localdomain")),
    ],
)
def test_parse_host(args, namespace):
    assert parse_args(args) == namespace


@pytest.mark.parametrize(
    "args,error_message",
    [
        (["-H"], "expected one argument"),
        (["--host"], "expected one argument"),
    ],
)
def test_parse_host_error(capsys, args: List[str], error_message: str):
    with pytest.raises(SystemExit):
        parse_args(args)
    captured = capsys.readouterr()
    assert error_message in captured.err


@pytest.mark.parametrize(
    "args,namespace",
    [
        (["-L", "INFO"], make_namespace(level=logging.INFO)),
        (["-L", "DEBUG"], make_namespace(level=logging.DEBUG)),
        (["-L", "WARNING"], make_namespace(level=logging.WARNING)),
        (["-L", "ERROR"], make_namespace(level=logging.ERROR)),
        (["--level", "INFO"], make_namespace(level=logging.INFO)),
        (["--level", "DEBUG"], make_namespace(level=logging.DEBUG)),
        (["--level", "WARNING"], make_namespace(level=logging.WARNING)),
        (["--level", "ERROR"], make_namespace(level=logging.ERROR)),
    ],
)
def test_parse_level(args, namespace):
    assert parse_args(args) == namespace


@pytest.mark.parametrize(
    "args,error_message",
    [
        (["-L", "NA"], "Invalid logging level"),
        (["-L"], "expected one argument"),
        (["--level", "NA"], "Invalid logging level"),
        (["--level"], "expected one argument"),
    ],
)
def test_parse_level_error(capsys, args: List[str], error_message: str):
    with pytest.raises(SystemExit):
        parse_args(args)
    captured = capsys.readouterr()
    assert error_message in captured.err


@pytest.mark.parametrize(
    "args,namespace",
    [(["-D"], make_namespace(debug=True)), (["--debug"], make_namespace(debug=True))],
)
def test_parse_debug(args, namespace):
    assert parse_args(args) == namespace


@pytest.mark.parametrize("args,message", [(["-h"], "usage"), (["--help"], "usage")])
def test_help(capsys, args, message):
    with pytest.raises(SystemExit):
        parse_args(args)
    captured = capsys.readouterr()
    assert message in captured.out
