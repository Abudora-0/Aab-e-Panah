# This file holds the Flask application.

from pathlib import Path

import mysql.connector
from flask import Flask, jsonify, request, send_from_directory

from backend.database.db_connection import get_connection, test_connection
from backend.database import request_repository
from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.app_logger import get_logger
from backend.logging_tools.audit_logger import AuditLogger
from backend.models.aid_request import AidRequest
from backend.services.request_service import RequestService


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
FRONTEND_FOLDER = PROJECT_FOLDER / "frontend"

app = Flask(__name__, static_folder=None)
logger = get_logger("app")
audit_logger = AuditLogger()
request_service = RequestService(audit_logger)


def camp_to_dict(camp):
    return {
        "camp_id": camp[0],
        "name": camp[1],
        "district": camp[2],
        "capacity": camp[3],
        "current_occupancy": camp[4],
        "created_at": camp[5].isoformat() if camp[5] else None,
    }


def request_to_dict(request, position=None):
    data = {
        "request_id": request.request_id,
        "area_name": request.area_name,
        "needs": request.needs,
        "severity": request.severity,
        "status": request.status,
        "created_at": request.created_at,
    }

    if position is not None:
        data["position"] = position

    if request.served_at is not None:
        data["served_at"] = request.served_at

    return data


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


@app.route("/api/requests")
def get_requests():
    waiting = request_service.waiting_requests()
    request_data = []
    position = 1

    for request in waiting:
        request_data.append(request_to_dict(request, position))
        position += 1

    return jsonify(
        {
            "requests": request_data,
            "waiting_count": request_service.waiting_count(),
        }
    )


@app.route("/api/requests", methods=["POST"])
def add_request():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        reason = "Request must contain JSON data"
        audit_logger.log_error("admin", ActionNames.ADD_REQUEST, "request", reason)
        return jsonify({"error": reason}), 400

    area_name = str(data.get("area_name", "")).strip()
    needs = str(data.get("needs", "")).strip()
    severity_value = data.get("severity")

    if not area_name or not needs:
        reason = "Area name and needs are required"
        audit_logger.log_error("admin", ActionNames.ADD_REQUEST, "request", reason)
        return jsonify({"error": reason}), 400

    if isinstance(severity_value, bool):
        severity_is_valid = False
    else:
        try:
            severity = int(severity_value)
            severity_is_valid = severity == severity_value and 1 <= severity <= 5
        except (TypeError, ValueError):
            severity_is_valid = False

    if not severity_is_valid:
        reason = "Severity must be a whole number from 1 to 5"
        audit_logger.log_error("admin", ActionNames.ADD_REQUEST, "request", reason)
        return jsonify({"error": reason}), 400

    request_item = AidRequest(None, area_name, needs, severity, "")

    try:
        request_service.add_request(request_item)
        logger.info("Added aid request %s", request_item.request_id)
        return jsonify(request_to_dict(request_item)), 201
    except mysql.connector.Error as error:
        logger.error("Could not add aid request: %s", error)
        audit_logger.log_error(
            "admin",
            ActionNames.SYSTEM_ERROR,
            "request",
            str(error),
        )
        return jsonify({"error": "Could not add request"}), 500


@app.route("/api/requests/serve-next", methods=["POST"])
def serve_next_request():
    request_item = request_service.serve_next()

    if request_item is None:
        return jsonify({"error": "No requests are waiting"}), 404

    return jsonify(request_to_dict(request_item))


@app.route("/api/requests/served")
def get_served_requests():
    try:
        served = request_repository.load_recent_served(10)
        return jsonify([request_to_dict(request) for request in served])
    except mysql.connector.Error as error:
        logger.error("Could not load served requests: %s", error)
        audit_logger.log_error(
            "admin",
            ActionNames.SYSTEM_ERROR,
            "served_requests",
            str(error),
        )
        return jsonify({"error": "Could not load served requests"}), 500


if __name__ == "__main__":
    app.run(debug=True)
