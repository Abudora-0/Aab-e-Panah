import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.logging_tools.audit_logger import AuditLogger


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
    log_file = PROJECT_FOLDER / "logs" / "test_audit_viewer.log"
    if log_file.exists():
        log_file.unlink()
    logger = AuditLogger(log_file=log_file)
    for index in range(8):
        result = "FAILED" if index == 2 else "SUCCESS"
        details = "detail " + str(index)
        if index == 4:
            details = "left | right"
        logger.log_action("tester", "ACTION_" + str(index), str(index), details, result)

    entries = logger.read_entries(5)
    check("last five entries", len(entries) == 5)
    check("newest first", entries[0]["action"] == "ACTION_7")
    check(
        "action filter",
        len(logger.read_entries(50, action="ACTION_4")) == 1,
    )
    check(
        "result filter",
        len(logger.read_entries(50, result="FAILED")) == 1,
    )
    with log_file.open("a", encoding="utf-8") as file:
        file.write("garbage line\n")
    entries = logger.read_entries(50)
    check("garbage line skipped", len(entries) == 8)
    check("separator in details kept", entries[3]["details"] == "left | right")
    missing_file = PROJECT_FOLDER / "logs" / "missing_audit_viewer.log"
    if missing_file.exists():
        missing_file.unlink()
    missing_logger = AuditLogger(log_file=missing_file)
    check("missing file is empty", missing_logger.read_entries() == [])

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
