import mysql.connector

from backend.database.db_connection import get_connection
from backend.logging_tools.app_logger import get_logger
from backend.models.camp import Camp


logger = get_logger("camp_repository")


def load_all_camps():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT camp_id, name, district, capacity, "
            "current_occupancy, created_at FROM camps "
            "ORDER BY created_at DESC, camp_id DESC"
        )
        camps = []
        for row in cursor.fetchall():
            camps.append(Camp(row[0], row[1], row[2], row[3], row[4], row[5]))
        return camps
    except mysql.connector.Error as error:
        logger.error("Could not load camps: %s", error)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
