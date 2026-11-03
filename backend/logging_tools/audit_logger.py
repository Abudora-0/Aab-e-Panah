# This file holds the audit logger.

import logging
from datetime import datetime
from pathlib import Path


LOG_FOLDER = Path(__file__).resolve().parents[2] / "logs"
AUDIT_FORMAT = "%(message)s"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class AuditLogger:
    def __init__(self, actor="admin", log_file=None):
        LOG_FOLDER.mkdir(parents=True, exist_ok=True)
        self.default_actor = actor
        self.recent_entries = []
        if log_file is None:
            log_file = LOG_FOLDER / "audit.log"
        else:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)

        logger_name = "aab.audit." + str(log_file)
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.FileHandler(
                log_file,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter(AUDIT_FORMAT))
            self.logger.addHandler(handler)

    def _add_entry(self, actor, action, target, details, result):
        entry = {
            "time": self._current_time(),
            "actor": actor,
            "action": action,
            "target": target,
            "result": result,
            "details": details,
        }
        self.recent_entries.append(entry)

        if len(self.recent_entries) > 100:
            self.recent_entries.pop(0)

        line = (
            f"{entry['time']} | {entry['actor']} | {entry['action']} | "
            f"{entry['target']} | {entry['result']} | {entry['details']}"
        )
        self.logger.info(line)

    def _current_time(self):
        return datetime.now().strftime(TIME_FORMAT)

    def log_action(
        self,
        actor,
        action,
        target,
        details="",
        result="SUCCESS",
    ):
        self._add_entry(actor, action, target, details, result)

    def log_error(self, actor, action, target, error_message):
        self._add_entry(actor, action, target, error_message, "FAILED")

    def log_exception(self, actor, action, target, exception):
        self.log_error(actor, action, target, str(exception))

    def get_recent(self, count=20):
        if count < 0:
            count = 0
        return list(reversed(self.recent_entries[-count:]))
