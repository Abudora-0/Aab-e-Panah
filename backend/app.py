# This file holds the Flask application.

from pathlib import Path

import mysql.connector
from flask import Flask, jsonify, request, send_from_directory

from backend.database.db_connection import get_connection, test_connection
from backend.database import camp_repository
from backend.database import request_repository
from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.app_logger import get_logger
from backend.logging_tools.audit_logger import AuditLogger
from backend.models.aid_request import AidRequest
from backend.services.request_service import RequestService
from backend.services.camp_service import CampService


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
FRONTEND_FOLDER = PROJECT_FOLDER / "frontend"
AREA_NAME_MAX = 100
NEEDS_MAX = 255
CAMP_NAME_MAX = 100
DISTRICT_MAX = 100

app = Flask(__name__, static_folder=None)
logger = get_logger("app")
audit_logger = AuditLogger()
request_service = RequestService(audit_logger)


def camp_to_dict(camp):
    return {
        "camp_id": camp.camp_id,
        "name": camp.name,
        "district": camp.district,
        "capacity": camp.capacity,
        "current_occupancy": camp.current_occupancy,
        "created_at": (
            camp.created_at.isoformat()
            if hasattr(camp.created_at, "isoformat")
            else camp.created_at
        ),
        "free_space": camp.free_space(),
    }


def request_to_dict(aid_request, position=None):
    data = {
        "request_id": aid_request.request_id,
        "area_name": aid_request.area_name,
        "needs": aid_request.needs,
        "severity": aid_request.severity,
        "status": aid_request.status,
        "created_at": aid_request.created_at,
    }

    if position is not None:
        data["position"] = position

    if aid_request.served_at is not None:
        data["served_at"] = aid_request.served_at

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
    try:
        camps = camp_repository.load_all_camps()
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

    length_checks = [
        (name, CAMP_NAME_MAX, "Camp name", ActionNames.ADD_CAMP),
        (district, DISTRICT_MAX, "District", ActionNames.ADD_CAMP),
    ]
    for value, maximum, label, action in length_checks:
        if len(value) > maximum:
            reason = label + " must be " + str(maximum) + " characters or less"
            audit_logger.log_error("admin", action, "camp", reason)
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

    for aid_request in waiting:
        request_data.append(request_to_dict(aid_request, position))
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

    if len(area_name) > AREA_NAME_MAX:
        reason = "Area name must be 100 characters or less"
        audit_logger.log_error("admin", ActionNames.ADD_REQUEST, "request", reason)
        return jsonify({"error": reason}), 400

    if len(needs) > NEEDS_MAX:
        reason = "Needs must be 255 characters or less"
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
        if request_service.last_error is not None:
            return jsonify({"error": "Could not serve request"}), 500
        return jsonify({"error": "No requests are waiting"}), 404

    return jsonify(request_to_dict(request_item))


@app.route("/api/requests/served")
def get_served_requests():
    try:
        served = request_repository.load_recent_served(10)
        return jsonify([request_to_dict(aid_request) for aid_request in served])
    except mysql.connector.Error as error:
        logger.error("Could not load served requests: %s", error)
        audit_logger.log_error(
            "admin",
            ActionNames.SYSTEM_ERROR,
            "served_requests",
            str(error),
        )
        return jsonify({"error": "Could not load served requests"}), 500


def _camp_service():
    return CampService(camp_repository.load_all_camps(), audit_logger)


@app.route("/api/camps/sorted")
def get_sorted_camps():
    field = request.args.get("sort", "name")
    order = request.args.get("order", "asc")
    algorithm = request.args.get("algorithm", "merge")
    if field not in ("name", "capacity", "free_space"):
        return jsonify({"error": "Invalid sort field"}), 400
    if order not in ("asc", "desc"):
        return jsonify({"error": "Invalid sort order"}), 400
    if algorithm not in ("merge", "quick"):
        return jsonify({"error": "Invalid sorting algorithm"}), 400
    try:
        camps, milliseconds = _camp_service().sort_camps(
            field,
            order,
            algorithm,
        )
        return jsonify(
            {
                "camps": [camp_to_dict(camp) for camp in camps],
                "algorithm": algorithm,
                "milliseconds": milliseconds,
            }
        )
    except mysql.connector.Error as error:
        logger.error("Could not sort camps: %s", error)
        return jsonify({"error": "Could not load camps"}), 500


@app.route("/api/camps/find")
def find_camp():
    free_space = request.args.get("free_space")
    name = request.args.get("name")
    service = None
    try:
        service = _camp_service()
        if free_space is not None:
            try:
                minimum = int(free_space)
            except (TypeError, ValueError):
                return jsonify({"error": "free_space must be a whole number"}), 400
            if minimum < 1:
                return jsonify({"error": "free_space must be at least 1"}), 400
            camp = service.find_camp_with_free_space(minimum)
        elif name is not None and name.strip():
            camp = service.find_camp_by_name(name.strip())
        else:
            return jsonify({"error": "Provide free_space or name"}), 400
        if camp is None:
            return jsonify({"error": "No camp found"}), 404
        return jsonify(camp_to_dict(camp))
    except mysql.connector.Error as error:
        logger.error("Could not find camp: %s", error)
        return jsonify({"error": "Could not load camps"}), 500


@app.route("/api/requests/ranked")
def get_ranked_requests():
    ranked = request_service.ranked_requests()
    request_data = []
    rank = 1
    for aid_request in ranked:
        data = request_to_dict(aid_request)
        data["rank"] = rank
        request_data.append(data)
        rank += 1
    return jsonify({"requests": request_data})


if __name__ == "__main__":
    app.run(debug=True)
