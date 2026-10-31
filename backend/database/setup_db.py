# This file sets up the database tables and sample data.

import sys
from pathlib import Path

import mysql.connector

PROJECT_FOLDER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.database.db_connection import get_connection
from backend.logging_tools.app_logger import get_logger


logger = get_logger("database_setup")


def run_sql_file(file_name):
    file_path = Path(__file__).resolve().parent / file_name
    sql_text = file_path.read_text(encoding="utf-8")
    statements = sql_text.split(";")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        for statement in statements:
            clean_statement = statement.strip()
            if clean_statement:
                cursor.execute(clean_statement)

        connection.commit()
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def main():
    try:
        print("Creating camps table...")
        run_sql_file("schema.sql")
        print("Camps table is ready.")

        print("Loading sample camps...")
        run_sql_file("sample_data.sql")
        print("Sample camps loaded.")
        print("Database setup complete.")
    except (OSError, mysql.connector.Error) as error:
        logger.error("Database setup failed: %s", error)
        print("Database setup failed:", error)


if __name__ == "__main__":
    main()
