# This file holds the Flask application.

from pathlib import Path

import mysql.connector
from flask import Flask, jsonify, request, send_from_directory

from backend.database.db_connection import get_connection, test_connection
from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.app_logger import get_logger
from backend.logging_tools.audit_logger import AuditLogger


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
FRONTEND_FOLDER = PROJECT_FOLDER / "frontend"

app = Flask(__name__, static_folder=None)
logger = get_logger("app")
audit_logger = AuditLogger()


def camp_to_dict(camp):
    return {
        "camp_id": camp[0],
        "name": camp[1],
        "district": camp[2],
        "capacity": camp[3],
        "current_occupancy": camp[4],
        "created_at": camp[5].isoformat() if camp[5] else None,
    }


@app.route("/")
def home():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/static/<path:file_name>")
def static_files(file_name):
    return send_from_directory(FRONTEND_FOLDER, file_name)


@app.route("/api/health")
def health():
    connected = test_connection()
    return jsonify({"database_connected": connected})


@app.route("/api/camps")
def get_camps():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT camp_id, name, district, capacity, "
            "current_occupancy, created_at "
            "FROM camps ORDER BY created_at DESC, camp_id DESC"
        )
        camps = cursor.fetchall()
        logger.info("Loaded %s camps", len(camps))
        return jsonify([camp_to_dict(camp) for camp in camps])
    except mysql.connector.Error as error:
        logger.error("Could not load camps: %s", error)
        audit_logger.log_error(
            "admin",
            ActionNames.SYSTEM_ERROR,
            "camps",
            str(error),
        )
        return jsonify({"error": "Could not load camps"}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


@app.route("/api/camps", methods=["POST"])
def add_camp():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        reason = "Request must contain JSON data"
        audit_logger.log_error("admin", ActionNames.ADD_CAMP, "camp", reason)
        return jsonify({"error": reason}), 400

    name = str(data.get("name", "")).strip()
    district = str(data.get("district", "")).strip()
    capacity_value = data.get("capacity")

    if not name or not district:
        reason = "Name and district are required"
        audit_logger.log_error("admin", ActionNames.ADD_CAMP, "camp", reason)
        return jsonify({"error": reason}), 400

    if isinstance(capacity_value, bool):
        capacity_is_valid = False
    else:
        try:
            capacity = int(capacity_value)
            capacity_is_valid = capacity == capacity_value and capacity > 0
        except (TypeError, ValueError):
            capacity_is_valid = False

    if not capacity_is_valid:
        reason = "Capacity must be a whole number above 0"
        audit_logger.log_error("admin", ActionNames.ADD_CAMP, "camp", reason)
        return jsonify({"error": reason}), 400

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
        logger.info("Added camp %s", camp_id)
        audit_logger.log_action(
            "admin",
            ActionNames.ADD_CAMP,
            str(camp_id),
            "Camp added",
        )
    except mysql.connector.Error as error:
        if connection is not None:
            connection.rollback()
        logger.error("Could not add camp: %s", error)
        audit_logger.log_error(
            "admin",
            ActionNames.SYSTEM_ERROR,
            "camp",
            str(error),
        )
        audit_logger.log_error(
            "admin",
            ActionNames.ADD_CAMP,
            "camp",
            "Database insert failed",
        )
        return jsonify({"error": "Could not add camp"}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

    return jsonify(
        {
            "camp_id": camp_id,
            "name": name,
            "district": district,
            "capacity": capacity,
            "current_occupancy": 0,
        }
    ), 201


if __name__ == "__main__":
    app.run(debug=True)
