# This file handles undo records.

from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.audit_logger import AuditLogger
from backend.structures.stack import Stack


class UndoManager:
    # This history is in memory and is lost when the app restarts.
    def __init__(self, audit_logger=None):
        self.actions = Stack()
        if audit_logger is None:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = audit_logger

    def record_action(self, action_name, target, details):
        record = {
            "action_name": action_name,
            "target": target,
            "details": details,
        }
        self.actions.push(record)

    def undo_last(self):
        record = self.actions.pop()

        if record is not None:
            self.audit_logger.log_action(
                "admin",
                ActionNames.UNDO_ACTION,
                str(record["target"]),
                record["details"],
            )

        return record

    def can_undo(self):
        return not self.actions.is_empty()

    def peek_last(self):
        return self.actions.peek()

    def history(self):
        records = self.actions.to_list()
        newest_first = []
        index = len(records) - 1
        while index >= 0:
            newest_first.append(records[index])
            index -= 1
        return newest_first

    def count(self):
        return self.actions.size()

    def clear(self):
        self.actions = Stack()
