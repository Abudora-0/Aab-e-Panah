# This file handles aid requests.

import mysql.connector

from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.audit_logger import AuditLogger
from backend.database import request_repository
from backend.logging_tools.app_logger import get_logger
from backend.structures.simple_queue import Queue


logger = get_logger("request_service")


class RequestService:
    def __init__(self, audit_logger=None, use_database=True):
        self.requests = Queue()
        self.use_database = use_database
        if audit_logger is None:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = audit_logger

        if self.use_database:
            try:
                waiting_requests = request_repository.load_waiting_requests()
                for request in waiting_requests:
                    self.requests.enqueue(request)
            except mysql.connector.Error as error:
                logger.error("Could not load requests at startup: %s", error)

    def add_request(self, request):
        if self.use_database:
            request.request_id = request_repository.insert_request(
                request.area_name,
                request.needs,
                request.severity,
            )

        self.requests.enqueue(request)
        self.audit_logger.log_action(
            "admin",
            ActionNames.ADD_REQUEST,
            str(request.request_id),
            "Aid request added",
        )

    def serve_next(self):
        request = self.requests.peek()

        if request is None:
            return None

        if self.use_database:
            try:
                served = request_repository.mark_request_served(
                    request.request_id
                )
                if not served:
                    logger.error("Request was not waiting in the database")
                    self.audit_logger.log_error(
                        "admin",
                        ActionNames.SYSTEM_ERROR,
                        str(request.request_id),
                        "Request was not waiting in the database",
                    )
                    return None
            except Exception as error:
                logger.error("Could not serve request: %s", error)
                self.audit_logger.log_error(
                    "admin",
                    ActionNames.SYSTEM_ERROR,
                    str(request.request_id),
                    str(error),
                )
                return None

        request = self.requests.dequeue()
        request.status = "SERVED"
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
