# This file tests the logging system.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.logging_tools.action_names import ActionNames
from backend.logging_tools.app_logger import get_logger
from backend.logging_tools.audit_logger import AuditLogger


def main():
    project_folder = Path(__file__).resolve().parents[1]
    log_folder = project_folder / "logs"

    logger = get_logger("test_logging")
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")

    audit_logger = AuditLogger()
    audit_logger.log_action(
        "admin",
        ActionNames.ADD_CAMP,
        "camp-1",
        "Camp added",
    )
    audit_logger.log_action(
        "admin",
        ActionNames.ADD_ROAD,
        "road-1",
        "Road added",
    )
    audit_logger.log_action(
        "admin",
        ActionNames.RUN_ROUTE,
        "route-1",
        "Route calculated",
    )
    audit_logger.log_error(
        "admin",
        ActionNames.SYSTEM_ERROR,
        "system",
        "Test failure",
    )

    print(audit_logger.get_recent(5))

    log_files_exist = (
        (log_folder / "app.log").exists()
        and (log_folder / "error.log").exists()
        and (log_folder / "audit.log").exists()
    )

    if log_files_exist:
        print("PASS")
    else:
        print("FAIL")


if __name__ == "__main__":
    main()
