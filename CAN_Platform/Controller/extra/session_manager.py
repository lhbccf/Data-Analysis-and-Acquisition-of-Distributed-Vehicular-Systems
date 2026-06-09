import logging
import threading

from services import Services


logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._current_session = None

    def start_new_session(self, description):
        with self._lock:
            if self._current_session is not None:
                Services.end_session(self._current_session.id)
                logger.info("Ended CAN DB session: %s", self._current_session.id)

            self._current_session = Services.create_session(description)
            logger.info("CAN DB session started: %s", self._current_session.id)
            return self._current_session

    def get_current_session(self):
        with self._lock:
            return self._current_session


session_manager = SessionManager()
