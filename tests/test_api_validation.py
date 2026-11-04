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

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
