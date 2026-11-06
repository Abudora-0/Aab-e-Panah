import mysql.connector

from backend.database.db_connection import get_connection
from backend.logging_tools.app_logger import get_logger
from backend.models.camp import Camp


logger = get_logger("camp_repository")


def insert_camp(name, district, capacity):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO camps (name, district, capacity) VALUES (%s, %s, %s)",
            (name, district, capacity),
        )
        connection.commit()
        camp_id = cursor.lastrowid
        cursor.execute(
            "SELECT created_at FROM camps WHERE camp_id = %s",
            (camp_id,),
        )
        row = cursor.fetchone()
        return camp_id, str(row[0])
    except mysql.connector.Error as error:
        logger.error("Could not insert camp: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def load_camp(camp_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT camp_id, name, district, capacity, "
            "current_occupancy, created_at FROM camps WHERE camp_id = %s",
            (camp_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Camp(row[0], row[1], row[2], row[3], row[4], row[5])
    except mysql.connector.Error as error:
        logger.error("Could not load camp: %s", error)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def delete_camp(camp_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM camps WHERE camp_id = %s", (camp_id,))
        connection.commit()
        return cursor.rowcount == 1
    except mysql.connector.Error as error:
        logger.error("Could not delete camp: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def change_occupancy(camp_id, change):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE camps SET current_occupancy = current_occupancy + %s "
            "WHERE camp_id = %s "
            "AND current_occupancy + %s >= 0 "
            "AND current_occupancy + %s <= capacity",
            (change, camp_id, change, change),
        )
        connection.commit()
        return cursor.rowcount == 1
    except mysql.connector.Error as error:
        logger.error("Could not change camp occupancy: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


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
