import mysql.connector

from backend.database.db_connection import get_connection
from backend.logging_tools.app_logger import get_logger
from backend.models.supply_batch import SupplyBatch


logger = get_logger("supply_repository")


def insert_supply(camp_id, item_name, quantity, expiry_days):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO supply_batches "
            "(camp_id, item_name, quantity, expiry_days) "
            "VALUES (%s, %s, %s, %s)",
            (camp_id, item_name, quantity, expiry_days),
        )
        connection.commit()
        return cursor.lastrowid
    except mysql.connector.Error as error:
        logger.error("Could not insert supply: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def load_supplies_for_camp(camp_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT batch_id, item_name, quantity, expiry_days "
            "FROM supply_batches WHERE camp_id = %s ORDER BY batch_id ASC",
            (camp_id,),
        )
        batches = []
        for row in cursor.fetchall():
            batches.append(SupplyBatch(row[0], row[1], row[2], row[3]))
        return batches
    except mysql.connector.Error as error:
        logger.error("Could not load supplies: %s", error)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def delete_supply(batch_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM supply_batches WHERE batch_id = %s",
            (batch_id,),
        )
        connection.commit()
        return cursor.rowcount == 1
    except mysql.connector.Error as error:
        logger.error("Could not delete supply: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def apply_supply_changes(updates, deletions):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        for batch_id, quantity in updates:
            cursor.execute(
                "UPDATE supply_batches SET quantity = %s "
                "WHERE batch_id = %s",
                (quantity, batch_id),
            )
        for batch_id in deletions:
            cursor.execute(
                "DELETE FROM supply_batches WHERE batch_id = %s",
                (batch_id,),
            )
        connection.commit()
    except mysql.connector.Error as error:
        logger.error("Could not apply supply changes: %s", error)
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
