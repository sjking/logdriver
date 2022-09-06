import logging
from logging import Logger
import queue
import signal
import socket
import pickle
import socketserver
import struct
from queue import Queue
from threading import Thread, Event
from time import sleep


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    def should_stop(self):
        if (
            hasattr(self.server, "stop")
            and isinstance(self.server.stop, Event)
            and self.server.stop.is_set()
        ):
            return True
        return False

    def handle(self):
        self.request.settimeout(1)
        while True:
            if self.should_stop():
                break
            try:
                chunk = self.connection.recv(4)
            except socket.timeout:
                continue
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            log_record = logging.makeLogRecord(obj)
            if hasattr(self.server, "queue") and isinstance(self.server.queue, Queue):
                self.server.queue.put(log_record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    def __init__(
        self,
        q: Queue,
        stop: Event,
        host: str,
        port: int,
        handler=LogRecordStreamHandler,
    ):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.queue = q
        self.stop = stop


class FileLogWriter(Thread):
    def __init__(self, q: Queue, stop: Event, logger: Logger):
        Thread.__init__(self)
        self.queue = q
        self.stop = stop
        self.logger = logger

    def run(self):
        while not self.stop.is_set():
            try:
                log_record = self.queue.get(timeout=1)
            except queue.Empty:
                pass
            else:
                self.logger.handle(log_record)
                self.queue.task_done()


def main(host: str, port: int, system_logger: Logger, user_logger: Logger):
    q = Queue()
    stop = Event()
    log_writer = FileLogWriter(q, stop, user_logger)
    log_writer.start()

    system_logger.warning("Starting TCP server")

    def stop_log_writer():
        stop.set()
        log_writer.join()

    try:
        tcp_server = LogRecordSocketReceiver(host=host, port=port, q=q, stop=stop)
    except OSError:
        stop_log_writer()
        raise

    def stop_server():
        stop_log_writer()
        tcp_server.shutdown()
        tcp_server.server_close()

    def shutdown(_pos, _frame):
        stop_server()

    signal.signal(signal.SIGINT, handler=shutdown)
    signal.signal(signal.SIGTERM, handler=shutdown)

    server_thread = Thread(target=tcp_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    while not stop.is_set():
        sleep(1)

    system_logger.warning("Shutting down TCP server")
