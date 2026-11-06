import sys
from pathlib import Path

import mysql.connector

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.database import camp_repository
from backend.logging_tools.audit_logger import AuditLogger
from backend.services.camp_service import CampService


failures = 0


def check(label, condition):
    global failures
    if condition:
        print("PASS:", label)
    else:
        print("FAIL:", label)
        failures += 1


def main():
    global failures
    camp_id = None
    service = CampService(
        [],
        AuditLogger(log_file=PROJECT_FOLDER / "logs" / "test_occupancy_audit.log"),
    )
    try:
        camp_id, created_at = camp_repository.insert_camp(
            "Occupancy Test Camp",
            "Test District",
            100,
        )
        result = service.register_arrival(camp_id, 30)
        camp = camp_repository.load_camp(camp_id)
        check("arrival succeeds", result["ok"])
        check("arrival occupancy is 30", camp.current_occupancy == 30)
        check("arrival free space is 70", camp.free_space() == 70)
        result = service.register_arrival(camp_id, 80)
        check("arrival above capacity refused", not result["ok"])
        result = service.register_arrival(camp_id, 70)
        camp = camp_repository.load_camp(camp_id)
        check("arrival fills camp", result["ok"] and camp.is_full())
        result = service.register_departure(camp_id, 20)
        camp = camp_repository.load_camp(camp_id)
        check("departure succeeds", result["ok"])
        check("departure occupancy is 80", camp.current_occupancy == 80)
        result = service.register_departure(camp_id, 200)
        check("departure above occupancy refused", not result["ok"])
        check("missing camp returns none", service.register_arrival(999999, 1) is None)
    except mysql.connector.Error as error:
        print("Database test failed:", error)
        failures += 1
    finally:
        if camp_id is not None:
            camp_repository.delete_camp(camp_id)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
