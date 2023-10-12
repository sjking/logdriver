# logdriver

Run a socket server for application logging.
Implemented as a CLI. Receives pickled LogRecord objects over a socket, 
buffers them, and handles them according to application requirements.

## Installation

```shell
pip install logdriver
```

## Example

Start `logdriver` on the command-line using default options. This will start the socket
server listening on `localhost` on port `9079`. It will use a `StreamLogger` to log
all the LogRecords it receives to `stdout`, and set the logging level to `WARNING`.

```shell
$ logdriver
Started logdriver logging socket server
Listening for logs on localhost:9079
Press CTRL+C to quit
Starting TCP server
```

In your Python application, configure your logger to use a `SocketHandler`:

```python
import logging
from logging.handlers import SocketHandler
handler = SocketHandler("localhost", 9079)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

logger.warning("Hello, world!")
```

You should see the log getting printed by the socket server.
