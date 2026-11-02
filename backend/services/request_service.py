# This file handles aid requests.

from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.audit_logger import AuditLogger
from backend.structures.simple_queue import Queue


class RequestService:
    def __init__(self, audit_logger=None):
        self.requests = Queue()
        if audit_logger is None:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = audit_logger

    def add_request(self, request):
        self.requests.enqueue(request)
        self.audit_logger.log_action(
            "admin",
            ActionNames.ADD_REQUEST,
            str(request.request_id),
            "Aid request added",
        )

    def serve_next(self):
        request = self.requests.dequeue()

        if request is not None:
            self.audit_logger.log_action(
                "admin",
                ActionNames.SERVE_REQUEST,
                str(request.request_id),
                "Aid request served",
            )

        return request

    def waiting_requests(self):
        return self.requests.to_list()

    def waiting_count(self):
        return self.requests.size()
