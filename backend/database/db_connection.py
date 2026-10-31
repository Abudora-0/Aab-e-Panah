# This file handles database connections.

import mysql.connector

from backend.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from backend.logging_tools.app_logger import get_logger


logger = get_logger("database")


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def test_connection():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True
    except mysql.connector.Error as error:
        logger.error("Database connection test failed: %s", error)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
