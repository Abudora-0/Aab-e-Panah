# This file handles aid requests.

import mysql.connector

from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.audit_logger import AuditLogger
from backend.database import request_repository
from backend.logging_tools.app_logger import get_logger
from backend.structures.simple_queue import Queue
from backend.algorithms.sorting import counting_sort_by_severity


logger = get_logger("request_service")


class RequestService:
    def __init__(self, audit_logger=None, use_database=True):
        self.requests = Queue()
        self.use_database = use_database
        if audit_logger is None:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = audit_logger
        self.loaded = False
        self.last_error = None

        if self.use_database:
            self.load_waiting_from_database()

    def load_waiting_from_database(self):
        try:
            waiting_requests = request_repository.load_waiting_requests()
            for request_item in waiting_requests:
                self.requests.enqueue(request_item)
            self.loaded = True
        except mysql.connector.Error as error:
            logger.error("Could not load requests from database: %s", error)
            self.loaded = False

    def add_request(self, request):
        if self.use_database:
            if not self.loaded:
                self.load_waiting_from_database()
            request_id, created_at = request_repository.insert_request(
                request.area_name,
                request.needs,
                request.severity,
            )
            request.request_id = request_id
            request.created_at = created_at

        self.requests.enqueue(request)
        self.audit_logger.log_action(
            "admin",
            ActionNames.ADD_REQUEST,
            str(request.request_id),
            "Aid request added",
        )

    def serve_next(self):
        self.last_error = None

        if self.use_database and not self.loaded:
            self.load_waiting_from_database()
            if not self.loaded:
                self.last_error = "Could not serve request"
                return None

        while True:
            request_item = self.requests.peek()
            if request_item is None:
                return None

            if self.use_database:
                try:
                    served = request_repository.mark_request_served(
                        request_item.request_id
                    )
                except mysql.connector.Error as error:
                    self.last_error = "Could not serve request"
                    logger.error("Could not serve request: %s", error)
                    self.audit_logger.log_error(
                        "admin",
                        ActionNames.SYSTEM_ERROR,
                        str(request_item.request_id),
                        str(error),
                    )
                    return None
                if not served:
                    logger.warning(
                        "Skipping stale request %s",
                        request_item.request_id,
                    )
                    self.requests.dequeue()
                    continue

            request_item = self.requests.dequeue()
            request_item.status = "SERVED"
            self.audit_logger.log_action(
                "admin",
                ActionNames.SERVE_REQUEST,
                str(request_item.request_id),
                "Aid request served",
            )
            return request_item

    def waiting_requests(self):
        if self.use_database and not self.loaded:
            self.load_waiting_from_database()
        return self.requests.to_list()

    def waiting_count(self):
        return self.requests.size()

    def ranked_requests(self):
        ranked = counting_sort_by_severity(
            self.waiting_requests(),
            descending=True,
        )
        self.audit_logger.log_action(
            "admin",
            ActionNames.RANK_REQUESTS,
            "requests",
            "Waiting requests ranked",
        )
        return ranked
