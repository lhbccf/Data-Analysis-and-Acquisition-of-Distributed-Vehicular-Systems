import logging
import queue
import threading


logger = logging.getLogger(__name__)
NEXTION_TERMINATOR = b"\xff\xff\xff"


class _WriteRequest:
    def __init__(self, serial_port, commands):
        self.serial_port = serial_port
        self.commands = tuple(commands)
        self.done = threading.Event()
        self.bytes_written = 0
        self.error = None


class NextionWriter:
    """Serialize all Nextion writes through one background worker.

    One queue item contains a complete command batch. This means a graph batch
    cannot be interleaved with live-value or session-list commands.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="NextionTxThread",
        )
        self._thread.start()

    @staticmethod
    def _write_command(serial_port, command):
        payload = command.encode()
        written = serial_port.write(payload)
        written_terminator = serial_port.write(NEXTION_TERMINATOR)
        return (
            (written if written is not None else len(payload))
            + (
                written_terminator
                if written_terminator is not None
                else len(NEXTION_TERMINATOR)
            )
        )

    def _worker(self):
        while True:
            request = self._queue.get()

            try:
                for command in request.commands:
                    request.bytes_written += self._write_command(
                        request.serial_port,
                        command,
                    )

                if hasattr(request.serial_port, "flush"):
                    request.serial_port.flush()
            except Exception as exc:
                request.error = exc
                logger.exception("Nextion serial write failed")
            finally:
                request.done.set()
                self._queue.task_done()

    def write_batch(self, serial_port, commands, wait=True, timeout=None):
        request = _WriteRequest(serial_port, commands)

        if not request.commands:
            return 0, 0

        self._queue.put(request)

        if not wait:
            return request

        if not request.done.wait(timeout):
            raise TimeoutError("Timed out waiting for Nextion write")

        if request.error is not None:
            raise request.error

        return request.bytes_written, len(request.commands)

    def write(self, serial_port, command, wait=True, timeout=None):
        result = self.write_batch(
            serial_port,
            (command,),
            wait=wait,
            timeout=timeout,
        )

        if wait:
            return result[0]

        return result


# Shared singleton, following the same pattern as signal_cache/session_manager.
nextion_writer = NextionWriter()
