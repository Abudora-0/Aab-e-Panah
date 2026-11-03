# This file stores aid requests in the database.

import mysql.connector

from backend.database.db_connection import get_connection
from backend.logging_tools.app_logger import get_logger
from backend.models.aid_request import AidRequest


logger = get_logger("request_repository")


def insert_request(area_name, needs, severity):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO aid_requests (area_name, needs, severity) "
            "VALUES (%s, %s, %s)",
            (area_name, needs, severity),
        )
        connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as error:
        logger.error("Could not insert aid request: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def row_to_request(row):
    return AidRequest(
        row[0],
        row[1],
        row[2],
        row[3],
        str(row[5]),
        row[4],
    )


def load_waiting_requests():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT request_id, area_name, needs, severity, status, created_at "
            "FROM aid_requests WHERE status = %s "
            "ORDER BY created_at ASC, request_id ASC",
            ("WAITING",),
        )
        return [row_to_request(row) for row in cursor.fetchall()]
    except mysql.connector.Error as error:
        logger.error("Could not load waiting requests: %s", error)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def mark_request_served(request_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE aid_requests SET status = %s, served_at = CURRENT_TIMESTAMP "
            "WHERE request_id = %s AND status = %s",
            ("SERVED", request_id, "WAITING"),
        )
        connection.commit()
        return cursor.rowcount == 1
    except mysql.connector.Error as error:
        logger.error("Could not serve aid request: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def load_recent_served(limit=10):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT request_id, area_name, needs, severity, status, created_at, "
            "served_at FROM aid_requests WHERE status = %s "
            "ORDER BY served_at DESC, request_id DESC LIMIT %s",
            ("SERVED", limit),
        )
        requests = []
        for row in cursor.fetchall():
            request = AidRequest(
                row[0],
                row[1],
                row[2],
                row[3],
                str(row[5]),
                row[4],
            )
            request.served_at = str(row[6])
            requests.append(request)
        return requests
    except mysql.connector.Error as error:
        logger.error("Could not load served requests: %s", error)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
