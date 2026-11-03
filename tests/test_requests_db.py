# This file tests database aid requests.

import sys
from pathlib import Path

import mysql.connector

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.database.db_connection import get_connection
from backend.logging_tools.audit_logger import AuditLogger
from backend.models.aid_request import AidRequest
from backend.services.request_service import RequestService


failures = 0


def check(label, condition):
    global failures

    if condition:
        print("PASS:", label)
    else:
        print("FAIL:", label)
        failures += 1


def delete_test_rows(request_ids):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        for request_id in request_ids:
            cursor.execute(
                "DELETE FROM aid_requests WHERE request_id = %s",
                (request_id,),
            )
        connection.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def main():
    global failures

    request_ids = []
    test_log = PROJECT_FOLDER / "logs" / "test_requests_audit.log"
    audit_logger = AuditLogger(log_file=test_log)

    try:
        service = RequestService(audit_logger, use_database=True)
        first = AidRequest(None, "Test Area One", "water", 5, "")
        second = AidRequest(None, "Test Area Two", "food", 3, "")
        service.add_request(first)
        service.add_request(second)
        request_ids.extend([first.request_id, second.request_id])

        waiting = service.waiting_requests()
        check("requests wait in arrival order", waiting[-2:] == [first, second])
        served = service.serve_next()
        check("first request is served", served == first)

        connection = None
        cursor = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT status FROM aid_requests WHERE request_id = %s",
                (first.request_id,),
            )
            row = cursor.fetchone()
            check("database row is served", row is not None and row[0] == "SERVED")
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()

        restarted_service = RequestService(audit_logger, use_database=True)
        remaining = restarted_service.waiting_requests()
        check("remaining request stays waiting", second in remaining)
    except mysql.connector.Error as error:
        print("Database test failed:", error)
        failures += 1
    finally:
        if request_ids:
            delete_test_rows(request_ids)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
