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


def query_waiting_ids():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT request_id FROM aid_requests WHERE status = %s",
            ("WAITING",),
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def restore_sample_rows(request_ids):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        for request_id in request_ids:
            cursor.execute(
                "UPDATE aid_requests SET status = %s, served_at = NULL "
                "WHERE request_id = %s",
                ("WAITING", request_id),
            )
        connection.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


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
    test_ids = []
    served_sample_ids = []
    sample_waiting_ids = []
    test_log = PROJECT_FOLDER / "logs" / "test_requests_audit.log"
    audit_logger = AuditLogger(log_file=test_log)

    try:
        sample_waiting_ids = query_waiting_ids()
        service = RequestService(audit_logger, use_database=True)
        first = AidRequest(None, "Test Area One", "water", 5, "")
        second = AidRequest(None, "Test Area Two", "food", 3, "")
        service.add_request(first)
        service.add_request(second)
        test_ids.extend([first.request_id, second.request_id])

        waiting = service.waiting_requests()
        check("first request has created time", bool(first.created_at))
        check("second request has created time", bool(second.created_at))
        check(
            "test requests are last in arrival order",
            [item.request_id for item in waiting[-2:]] == test_ids,
        )

        served = None
        while served is None or served.request_id != first.request_id:
            served = service.serve_next()
            if served is None:
                break
            if served.request_id not in test_ids:
                served_sample_ids.append(served.request_id)
        check("first request is served", served is not None and served.request_id == first.request_id)

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
        remaining_ids = [
            item.request_id for item in restarted_service.waiting_requests()
        ]
        check("second request stays waiting", second.request_id in remaining_ids)
    except mysql.connector.Error as error:
        print("Database test failed:", error)
        failures += 1
    finally:
        if served_sample_ids:
            restore_sample_rows(served_sample_ids)
        if test_ids:
            delete_test_rows(test_ids)
        if sample_waiting_ids:
            check(
                "sample waiting rows restored",
                query_waiting_ids() == sample_waiting_ids,
            )

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
