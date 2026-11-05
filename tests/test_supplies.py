import sys
from pathlib import Path

import mysql.connector

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.database import camp_repository
from backend.database import supply_repository
from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.audit_logger import AuditLogger
from backend.services.supply_service import SupplyService
from backend.services.undo_manager import UndoManager
from backend.services.undo_service import UndoService


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
    test_camp_id = None
    audit_logger = AuditLogger(
        log_file=PROJECT_FOLDER / "logs" / "test_supplies_audit.log"
    )
    undo_manager = UndoManager(audit_logger)
    undo_service = UndoService(undo_manager, audit_logger)
    supply_service = SupplyService(undo_manager, audit_logger)

    try:
        test_camp_id, created_at = camp_repository.insert_camp(
            "Supply Test Camp",
            "Test District",
            100,
        )
        first = supply_service.add_supply(test_camp_id, "Water", 10, 30)
        second = supply_service.add_supply(test_camp_id, "Water", 5, 10)
        third = supply_service.add_supply(test_camp_id, "Rice", 8, 90)
        camp = supply_service.load_camp_with_supplies(test_camp_id)
        batches = camp.supply_list()
        check(
            "supplies keep arrival order",
            [batch.batch_id for batch in batches]
            == [first.batch_id, second.batch_id, third.batch_id],
        )

        result = supply_service.issue_supplies(test_camp_id, "water", 7)
        check("issue uses soonest expiry", result["ok"])
        camp = supply_service.load_camp_with_supplies(test_camp_id)
        water = []
        for batch in camp.supply_list():
            if batch.item_name.lower() == "water":
                water.append(batch)
        check("short water batch is gone", len(water) == 1)
        check("older water batch has eight", water[0].quantity == 8)
        database_batches = supply_repository.load_supplies_for_camp(test_camp_id)
        check(
            "database matches issue",
            len(database_batches) == 2
            and database_batches[0].quantity == 8,
        )

        before = [(batch.batch_id, batch.quantity) for batch in database_batches]
        result = supply_service.issue_supplies(test_camp_id, "Water", 100)
        check("too much water refused", not result["ok"])
        after = supply_repository.load_supplies_for_camp(test_camp_id)
        check("refused issue changes nothing", before == [
            (batch.batch_id, batch.quantity) for batch in after
        ])
        result = supply_service.issue_supplies(test_camp_id, "Unknown", 1)
        check("unknown item refused", not result["ok"])
        check("undo history cleared after issue", undo_manager.count() == 0)

        extra = supply_service.add_supply(test_camp_id, "Tents", 2, 20)
        result = undo_service.perform_undo()
        check("undo removes added supply", extra.batch_id not in [
            batch.batch_id
            for batch in supply_repository.load_supplies_for_camp(test_camp_id)
        ])
        undo_manager.record_action(
            ActionNames.ADD_CAMP,
            str(test_camp_id),
            "Supply Test Camp",
        )
        result = undo_service.perform_undo()
        check("undo removes camp", camp_repository.load_camp(test_camp_id) is None)
    except mysql.connector.Error as error:
        print("Database test failed:", error)
        failures += 1
    finally:
        if test_camp_id is not None:
            camp_repository.delete_camp(test_camp_id)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
