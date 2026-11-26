import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

# Set this before importing the app so tests do not use the real log.
os.environ["AUDIT_LOG_FILE"] = str(PROJECT_FOLDER / "logs" / "test_api_audit.log")

from backend.app import app
from backend.database import camp_repository


failures = 0


def raise_api_error():
    raise RuntimeError("test error")


app.add_url_rule(
    "/api/test-server-error",
    "test_api_server_error",
    raise_api_error,
)


def check(label, condition):
    global failures
    if condition:
        print("PASS:", label)
    else:
        print("FAIL:", label)
        failures += 1


def main():
    client = app.test_client()
    request_base = {"area_name": "Area", "needs": "Water", "severity": 1}
    unicode_characters = ("\u2028", "\u2029", "\u0085")
    response = client.post(
        "/api/requests",
        json=dict(request_base, area_name="A" * 101),
    )
    check("long area name refused", response.status_code == 400)
    with patch("backend.app.request_service.add_request") as add_request:
        response = client.post(
            "/api/requests",
            json=dict(request_base, area_name="Area\nforged audit line"),
        )
        check("line break in area name refused", response.status_code == 400)
        check("area line break has no database write", not add_request.called)
    response = client.post(
        "/api/requests",
        json=dict(request_base, needs="N" * 256),
    )
    check("long needs refused", response.status_code == 400)
    with patch("backend.app.request_service.add_request") as add_request:
        response = client.post(
            "/api/requests",
            json=dict(request_base, needs="Water\rforged audit line"),
        )
        check("line break in needs refused", response.status_code == 400)
        check("needs line break has no database write", not add_request.called)
    for character in unicode_characters:
        with patch("backend.app.request_service.add_request") as add_request:
            response = client.post(
                "/api/requests",
                json=dict(
                    request_base,
                    area_name="Area" + character + "name",
                ),
            )
            check(
                "Unicode area name refused",
                response.status_code == 400,
            )
            check("Unicode area name has no database write", not add_request.called)
        with patch("backend.app.request_service.add_request") as add_request:
            response = client.post(
                "/api/requests",
                json=dict(request_base, needs="Water" + character + "need"),
            )
            check("Unicode needs refused", response.status_code == 400)
            check("Unicode needs has no database write", not add_request.called)
    response = client.post(
        "/api/camps",
        json={"name": "C" * 101, "district": "D", "capacity": 1},
    )
    check("long camp name refused", response.status_code == 400)
    with patch("backend.app.camp_repository.insert_camp") as insert_camp:
        response = client.post(
            "/api/camps",
            json={"name": "Camp\tname", "district": "D", "capacity": 1},
        )
        check("control character in camp name refused", response.status_code == 400)
        check("camp name line break has no database write", not insert_camp.called)
    with patch("backend.app.camp_repository.insert_camp") as insert_camp:
        response = client.post(
            "/api/camps",
            json={"name": "Camp", "district": "D\nistrict", "capacity": 1},
        )
        check("line break in district refused", response.status_code == 400)
        check("district line break has no database write", not insert_camp.called)
    for character in unicode_characters:
        with patch("backend.app.camp_repository.insert_camp") as insert_camp:
            response = client.post(
                "/api/camps",
                json={
                    "name": "Camp" + character + "name",
                    "district": "D",
                    "capacity": 1,
                },
            )
            check("Unicode camp name refused", response.status_code == 400)
            check("Unicode camp name has no database write", not insert_camp.called)
        with patch("backend.app.camp_repository.insert_camp") as insert_camp:
            response = client.post(
                "/api/camps",
                json={
                    "name": "Camp",
                    "district": "D" + character + "istrict",
                    "capacity": 1,
                },
            )
            check("Unicode district refused", response.status_code == 400)
            check("Unicode district has no database write", not insert_camp.called)
    response = client.post(
        "/api/camps",
        json={"name": "Camp", "district": "D", "capacity": 0},
    )
    check("zero capacity refused", response.status_code == 400)
    response = client.post(
        "/api/camps",
        json={"name": "Camp", "district": "D", "capacity": 100001},
    )
    check("capacity above maximum refused", response.status_code == 400)
    check(
        "capacity above maximum has exact message",
        response.json["error"]
        == "Capacity must be a whole number from 1 to 100000",
    )
    response = client.post(
        "/api/camps",
        json={"name": "Camp", "district": "D", "capacity": 99999999999},
    )
    check("very large capacity refused", response.status_code == 400)
    with patch(
        "backend.app.camp_repository.camp_exists_by_name_and_district",
        return_value=False,
    ), patch(
        "backend.app.camp_repository.insert_camp",
        return_value=(1, "2026-01-01 00:00:00"),
    ), patch("backend.app.undo_manager.record_action"), patch(
        "backend.app.audit_logger.log_action"
    ):
        response = client.post(
            "/api/camps",
            json={"name": "Capacity limit", "district": "D", "capacity": 100000},
        )
        check("maximum capacity is accepted", response.status_code == 201)
        check("maximum capacity is returned", response.json["capacity"] == 100000)
    with patch(
        "backend.app.camp_repository.camp_exists_by_name_and_district",
        return_value=True,
    ) as camp_exists, patch(
        "backend.app.camp_repository.insert_camp"
    ) as insert_camp:
        response = client.post(
            "/api/camps",
            json={"name": "cAMP", "district": "d", "capacity": 1},
        )
        check("duplicate camp refused", response.status_code == 409)
        check(
            "duplicate camp has exact message",
            response.json["error"]
            == "A camp with this name and district already exists",
        )
        check(
            "duplicate camp check uses submitted name and district",
            camp_exists.call_args.args == ("cAMP", "d"),
        )
        check("duplicate camp is not inserted", not insert_camp.called)
    fake_connection = Mock()
    fake_cursor = Mock()
    fake_cursor.fetchone.return_value = None
    fake_connection.cursor.return_value = fake_cursor
    with patch(
        "backend.database.camp_repository.get_connection",
        return_value=fake_connection,
    ):
        exists = camp_repository.camp_exists_by_name_and_district("Camp", "D")
        query = fake_cursor.execute.call_args.args[0]
        parameters = fake_cursor.execute.call_args.args[1]
        check("duplicate lookup returns no match", not exists)
        check("duplicate lookup uses one query", fake_cursor.execute.call_count == 1)
        check(
            "duplicate lookup uses case-insensitive SQL and placeholders",
            "LOWER(name) = LOWER(%s)" in query
            and "LOWER(district) = LOWER(%s)" in query
            and parameters == ("Camp", "D"),
        )
    response = client.post(
        "/api/requests",
        json=dict(request_base, severity=6),
    )
    check("severity six refused", response.status_code == 400)
    response = client.post(
        "/api/requests",
        json=dict(request_base, area_name=""),
    )
    check("blank area refused", response.status_code == 400)
    supply_url = "/api/camps/999999/supplies"
    response = client.post(supply_url, json={"quantity": 1, "expiry_days": 1})
    check("missing item name refused", response.status_code == 400)
    response = client.post(
        supply_url,
        json={"item_name": "Water", "quantity": 0, "expiry_days": 1},
    )
    check("zero supply quantity refused", response.status_code == 400)
    response = client.post(
        supply_url,
        json={"item_name": "Water", "quantity": 100001, "expiry_days": 1},
    )
    check("large supply quantity refused", response.status_code == 400)
    response = client.post(
        supply_url,
        json={"item_name": "Water", "quantity": 1, "expiry_days": -1},
    )
    check("negative expiry refused", response.status_code == 400)
    response = client.post(
        "/api/camps/999999/supplies/issue",
        json={"item_name": "Water", "amount": 0},
    )
    check("zero issue amount refused", response.status_code == 400)
    response = client.post(
        supply_url,
        json={"item_name": "I" * 101, "quantity": 1, "expiry_days": 1},
    )
    check("long item name refused", response.status_code == 400)
    with patch("backend.app.supply_service.add_supply") as add_supply:
        response = client.post(
            supply_url,
            json={
                "item_name": "Water\nfake audit",
                "quantity": 1,
                "expiry_days": 1,
            },
        )
        check("line break in added item name refused", response.status_code == 400)
        check("added item line break has no database write", not add_supply.called)
    with patch("backend.app.supply_service.issue_supplies") as issue_supplies:
        response = client.post(
            "/api/camps/999999/supplies/issue",
            json={"item_name": "Water\nfake audit", "amount": 1},
        )
        check(
            "line break in issued item name refused",
            response.status_code == 400,
        )
        check(
            "issued item line break has no database write",
            not issue_supplies.called,
        )
    for character in unicode_characters:
        with patch("backend.app.supply_service.add_supply") as add_supply:
            response = client.post(
                supply_url,
                json={
                    "item_name": "Water" + character + "item",
                    "quantity": 1,
                    "expiry_days": 1,
                },
            )
            check("Unicode added item name refused", response.status_code == 400)
            check("Unicode added item has no database write", not add_supply.called)
        with patch("backend.app.supply_service.issue_supplies") as issue_supplies:
            response = client.post(
                "/api/camps/999999/supplies/issue",
                json={"item_name": "Water" + character + "item", "amount": 1},
            )
            check("Unicode issued item name refused", response.status_code == 400)
            check(
                "Unicode issued item has no database write",
                not issue_supplies.called,
            )
    occupancy_url = "/api/camps/999999/arrivals"
    for label, value in (
        ("zero people refused", 0),
        ("decimal people refused", 2.5),
        ("text people refused", "many"),
        ("large people refused", 100001),
    ):
        response = client.post(occupancy_url, json={"people": value})
        check(label, response.status_code == 400)
    response = client.get("/api/audit?count=0")
    check("audit zero count refused", response.status_code == 400)
    response = client.get("/api/audit?action=NOT_AN_ACTION")
    check("audit unknown action refused", response.status_code == 400)
    response = client.get("/api/audit?result=UNKNOWN")
    check("audit unknown result refused", response.status_code == 400)
    response = client.get("/api/not-found")
    check("API 404 uses JSON", response.status_code == 404
          and response.is_json and "error" in response.json)
    response = client.post("/api/health")
    check("API 405 uses JSON", response.status_code == 405
          and response.is_json and "error" in response.json)
    response = client.get("/not-found")
    check("non-API 404 keeps HTML", response.status_code == 404
          and not response.is_json)

    response = client.get("/api/test-server-error")
    check("API 500 uses JSON", response.status_code == 500
          and response.is_json and "error" in response.json)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
