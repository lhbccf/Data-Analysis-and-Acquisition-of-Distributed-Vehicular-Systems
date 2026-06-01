import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s [%(threadName)s] %(levelname)s %(name)s: %(message)s"


def configure_logging():
    controller_dir = Path(__file__).resolve().parents[1]
    log_dir = controller_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "controller.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if not getattr(root_logger, "_controller_file_logging", False):
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(file_handler)
        root_logger._controller_file_logging = True

    has_console_handler = any(
        type(handler) is logging.StreamHandler
        for handler in root_logger.handlers
    )

    if not has_console_handler:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(stream_handler)

    return log_path
