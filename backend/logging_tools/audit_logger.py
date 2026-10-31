# This file holds the audit logger.

import logging
from pathlib import Path


LOG_FOLDER = Path(__file__).resolve().parents[2] / "logs"
AUDIT_FORMAT = "%(message)s"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class AuditLogger:
    def __init__(self, actor="admin"):
        LOG_FOLDER.mkdir(parents=True, exist_ok=True)
        self.default_actor = actor
        self.recent_entries = []
        self.logger = logging.getLogger("aab.audit")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not getattr(self.logger, "_aab_audit_configured", False):
            handler = logging.FileHandler(
                LOG_FOLDER / "audit.log",
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter(AUDIT_FORMAT))
            self.logger.addHandler(handler)
            self.logger._aab_audit_configured = True

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
        from datetime import datetime

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
