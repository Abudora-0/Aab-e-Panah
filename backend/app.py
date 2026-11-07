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
from backend.services.supply_service import SupplyService
from backend.services.undo_manager import UndoManager
from backend.services.undo_service import UndoService


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
FRONTEND_FOLDER = PROJECT_FOLDER / "frontend"
AREA_NAME_MAX = 100
NEEDS_MAX = 255
CAMP_NAME_MAX = 100
DISTRICT_MAX = 100
ITEM_NAME_MAX = 100
QUANTITY_MAX = 100000
EXPIRY_MAX = 3650

app = Flask(__name__, static_folder=None)
logger = get_logger("app")
audit_logger = AuditLogger()
request_service = RequestService(audit_logger)
undo_manager = UndoManager(audit_logger)
undo_service = UndoService(undo_manager, audit_logger)
supply_service = SupplyService(undo_manager, audit_logger)


def has_control_characters(text):
    for character in text:
        if ord(character) < 32 or ord(character) == 127:
            return True
    return False


def camp_to_dict(camp):
    return {
        "camp_id": camp.camp_id,
        "name": camp.name,
        "district": camp.district,
        "capacity": camp.capacity,
        "current_occupancy": camp.current_occupancy,
        "created_at": str(camp.created_at) if camp.created_at else None,
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


def supply_to_dict(batch):
    return {
        "batch_id": batch.batch_id,
        "item_name": batch.item_name,
        "quantity": batch.quantity,
        "expiry_days": batch.expiry_days,
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

    for value, label in ((name, "Camp name"), (district, "District")):
        if has_control_characters(value):
            reason = label + " cannot contain line breaks"
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

    try:
        camp_id, created_at = camp_repository.insert_camp(
            name,
            district,
            capacity,
        )
        logger.info("Added camp %s", camp_id)
        undo_manager.record_action(
            ActionNames.ADD_CAMP,
            str(camp_id),
            name,
        )
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
    return jsonify(
        {
            "camp_id": camp_id,
            "name": name,
            "district": district,
            "capacity": capacity,
            "current_occupancy": 0,
            "created_at": created_at,
            "free_space": capacity,
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

    for value, label in ((area_name, "Area name"), (needs, "Needs")):
        if has_control_characters(value):
            reason = label + " cannot contain line breaks"
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


@app.route("/api/camps/<int:camp_id>/supplies")
def get_supplies(camp_id):
    try:
        camp = supply_service.load_camp_with_supplies(camp_id)
        if camp is None:
            return jsonify({"error": "Camp not found"}), 404
        return jsonify(
            {
                **camp_to_dict(camp),
                "supplies": [
                    supply_to_dict(batch) for batch in camp.supply_list()
                ],
            }
        )
    except mysql.connector.Error as error:
        logger.error("Could not load supplies: %s", error)
        return jsonify({"error": "Could not load supplies"}), 500


def validate_supply_number(value, label, maximum, allow_zero):
    if isinstance(value, bool):
        return None, label + " must be a whole number"
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None, label + " must be a whole number"
    if number != value:
        return None, label + " must be a whole number"
    minimum = 0 if allow_zero else 1
    if number < minimum or number > maximum:
        if allow_zero:
            return None, label + " must be from 0 to " + str(maximum)
        return None, label + " must be from 1 to " + str(maximum)
    return number, None


@app.route("/api/camps/<int:camp_id>/supplies", methods=["POST"])
def add_supply(camp_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        reason = "Request must contain JSON data"
        audit_logger.log_error("admin", ActionNames.ADD_SUPPLY, "supply", reason)
        return jsonify({"error": reason}), 400
    item_name = str(data.get("item_name", "")).strip()
    if not item_name:
        reason = "Item name is required"
        audit_logger.log_error("admin", ActionNames.ADD_SUPPLY, "supply", reason)
        return jsonify({"error": reason}), 400
    if has_control_characters(item_name):
        reason = "Item name cannot contain line breaks"
        audit_logger.log_error("admin", ActionNames.ADD_SUPPLY, "supply", reason)
        return jsonify({"error": reason}), 400
    if len(item_name) > ITEM_NAME_MAX:
        reason = "Item name must be 100 characters or less"
        audit_logger.log_error("admin", ActionNames.ADD_SUPPLY, "supply", reason)
        return jsonify({"error": reason}), 400
    quantity, reason = validate_supply_number(
        data.get("quantity"),
        "Quantity",
        QUANTITY_MAX,
        False,
    )
    if reason is not None:
        audit_logger.log_error("admin", ActionNames.ADD_SUPPLY, "supply", reason)
        return jsonify({"error": reason}), 400
    expiry_days, reason = validate_supply_number(
        data.get("expiry_days"),
        "Expiry days",
        EXPIRY_MAX,
        True,
    )
    if reason is not None:
        audit_logger.log_error("admin", ActionNames.ADD_SUPPLY, "supply", reason)
        return jsonify({"error": reason}), 400
    try:
        batch = supply_service.add_supply(
            camp_id,
            item_name,
            quantity,
            expiry_days,
        )
        if batch is None:
            return jsonify({"error": "Camp not found"}), 404
        return jsonify(supply_to_dict(batch)), 201
    except mysql.connector.Error as error:
        logger.error("Could not add supply: %s", error)
        return jsonify({"error": "Could not add supply"}), 500


@app.route("/api/camps/<int:camp_id>/supplies/issue", methods=["POST"])
def issue_supplies(camp_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        reason = "Request must contain JSON data"
        audit_logger.log_error(
            "admin",
            ActionNames.ISSUE_SUPPLIES,
            "supply",
            reason,
        )
        return jsonify({"error": reason}), 400
    item_name = str(data.get("item_name", "")).strip()
    if not item_name:
        reason = "Item name is required"
        audit_logger.log_error(
            "admin",
            ActionNames.ISSUE_SUPPLIES,
            "supply",
            reason,
        )
        return jsonify({"error": reason}), 400
    if has_control_characters(item_name):
        reason = "Item name cannot contain line breaks"
        audit_logger.log_error(
            "admin",
            ActionNames.ISSUE_SUPPLIES,
            "supply",
            reason,
        )
        return jsonify({"error": reason}), 400
    if len(item_name) > ITEM_NAME_MAX:
        reason = "Item name must be 100 characters or less"
        audit_logger.log_error(
            "admin",
            ActionNames.ISSUE_SUPPLIES,
            "supply",
            reason,
        )
        return jsonify({"error": reason}), 400
    amount, reason = validate_supply_number(
        data.get("amount"),
        "Amount",
        QUANTITY_MAX,
        False,
    )
    if reason is not None:
        audit_logger.log_error(
            "admin",
            ActionNames.ISSUE_SUPPLIES,
            "supply",
            reason,
        )
        return jsonify({"error": reason}), 400
    try:
        result = supply_service.issue_supplies(camp_id, item_name, amount)
        if result is None:
            return jsonify({"error": "Camp not found"}), 404
        if not result["ok"]:
            return jsonify({"error": result["message"]}), 400
        return jsonify(result)
    except mysql.connector.Error as error:
        logger.error("Could not issue supplies: %s", error)
        return jsonify({"error": "Could not issue supplies"}), 500


@app.route("/api/undo/history")
def get_undo_history():
    history = []
    for record in undo_manager.history():
        history.append(
            {
                "action": record["action_name"],
                "target": record["target"],
                "details": record["details"],
            }
        )
    return jsonify({"history": history, "count": undo_manager.count()})


@app.route("/api/undo", methods=["POST"])
def perform_undo():
    try:
        result = undo_service.perform_undo()
        if result is None:
            return jsonify({"error": "Nothing to undo"}), 404
        return jsonify(result)
    except mysql.connector.Error as error:
        logger.error("Could not undo action: %s", error)
        return jsonify({"error": "Could not undo action"}), 500


def register_occupancy(camp_id, action_name):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        reason = "Request must contain JSON data"
        audit_logger.log_error("admin", action_name, str(camp_id), reason)
        return jsonify({"error": reason}), 400
    people, reason = validate_supply_number(
        data.get("people"),
        "People",
        100000,
        False,
    )
    if reason is not None:
        audit_logger.log_error("admin", action_name, str(camp_id), reason)
        return jsonify({"error": reason}), 400
    try:
        service = CampService([], audit_logger)
        if action_name == ActionNames.REGISTER_ARRIVAL:
            result = service.register_arrival(camp_id, people)
        else:
            result = service.register_departure(camp_id, people)
        if result is None:
            return jsonify({"error": "Camp not found"}), 404
        if not result["ok"]:
            return jsonify({"error": result["message"]}), 400
        return jsonify(result)
    except mysql.connector.Error as error:
        logger.error("Could not update occupancy: %s", error)
        return jsonify({"error": "Could not update camp occupancy"}), 500


@app.route("/api/camps/<int:camp_id>/arrivals", methods=["POST"])
def register_arrivals(camp_id):
    return register_occupancy(camp_id, ActionNames.REGISTER_ARRIVAL)


@app.route("/api/camps/<int:camp_id>/departures", methods=["POST"])
def register_departures(camp_id):
    return register_occupancy(camp_id, ActionNames.REGISTER_DEPARTURE)


@app.route("/api/audit")
def get_audit_entries():
    count_text = request.args.get("count", "50")
    try:
        count = int(count_text)
    except (TypeError, ValueError):
        return jsonify({"error": "Count must be a whole number from 1 to 200"}), 400
    if count < 1 or count > 200 or str(count) != count_text:
        return jsonify({"error": "Count must be a whole number from 1 to 200"}), 400

    action = request.args.get("action")
    if action == "all":
        action = None
    elif action is not None and action not in ActionNames.all_names():
        return jsonify({"error": "Unknown audit action"}), 400

    result = request.args.get("result")
    if result == "all":
        result = None
    elif result not in ("SUCCESS", "FAILED", None):
        return jsonify({"error": "Result must be SUCCESS or FAILED"}), 400

    entries = audit_logger.read_entries(count, action, result)
    return jsonify({"entries": entries, "count": len(entries)})


if __name__ == "__main__":
    app.run(debug=True)
