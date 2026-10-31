# This file tests the database connection.

import sys
from pathlib import Path

import mysql.connector

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.database.db_connection import get_connection, test_connection


def main():
    connection = None
    cursor = None

    try:
        connection_works = test_connection()
        if not connection_works:
            print("FAIL")
            return

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM camps")
        row = cursor.fetchone()
        camp_count = row[0]
        print("Database connection works.")
        print("Camps in table:", camp_count)
        print("PASS")
    except mysql.connector.Error as error:
        print("Database test failed:", error)
        print("FAIL")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
