import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.app import app


failures = 0


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
    response = client.post(
        "/api/requests",
        json=dict(request_base, area_name="A" * 101),
    )
    check("long area name refused", response.status_code == 400)
    response = client.post(
        "/api/requests",
        json=dict(request_base, needs="N" * 256),
    )
    check("long needs refused", response.status_code == 400)
    response = client.post(
        "/api/camps",
        json={"name": "C" * 101, "district": "D", "capacity": 1},
    )
    check("long camp name refused", response.status_code == 400)
    response = client.post(
        "/api/camps",
        json={"name": "Camp", "district": "D", "capacity": 0},
    )
    check("zero capacity refused", response.status_code == 400)
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

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
