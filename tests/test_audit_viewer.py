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
    check("zero recent entries", logger.get_recent(0) == [])
    recent_entries = logger.get_recent(2)
    check(
        "two recent entries newest first",
        len(recent_entries) == 2
        and recent_entries[0]["action"] == "ACTION_7"
        and recent_entries[1]["action"] == "ACTION_6",
    )
    missing_file = PROJECT_FOLDER / "logs" / "missing_audit_viewer.log"
    if missing_file.exists():
        missing_file.unlink()
    missing_logger = AuditLogger(log_file=missing_file)
    check("missing file is empty", missing_logger.read_entries() == [])

    cases = [
        ("log_action", "ACTION | BAD", "action details"),
        ("log_error", "ERROR_ACTION", "error details"),
        ("log_exception", "EXCEPTION_ACTION", "exception details"),
    ]
    for index, case in enumerate(cases):
        case_name, action, ending = case
        case_file = PROJECT_FOLDER / "logs" / (
            "test_audit_" + str(index) + ".log"
        )
        if case_file.exists():
            case_file.unlink()
        case_logger = AuditLogger(log_file=case_file)
        details = "first\n2026 | forged audit line\r\t" + ending
        if case_name == "log_action":
            case_logger.log_action("tester", action, "target", details)
        elif case_name == "log_error":
            case_logger.log_error("tester", action, "target", details)
        else:
            case_logger.log_exception(
                "tester",
                action,
                "target",
                Exception(details),
            )
        lines = case_file.read_text(encoding="utf-8").splitlines()
        entries = case_logger.read_entries()
        check(case_name + " writes one line", len(lines) == 1)
        check(case_name + " reads one entry", len(entries) == 1)
        check(
            case_name + " keeps text in one entry",
            "\n" not in entries[0]["details"]
            and "\r" not in entries[0]["details"]
            and "\t" not in entries[0]["details"]
            and "forged audit line" in entries[0]["details"],
        )
        if case_name == "log_action":
            check(
                "separator in action kept in one entry",
                entries[0]["action"] == "ACTION / BAD"
                and len(entries[0]) == 6,
            )

    unicode_characters = ("\u2028", "\u2029", "\u0085")
    for index, character in enumerate(unicode_characters):
        unicode_file = PROJECT_FOLDER / "logs" / (
            "test_unicode_audit_" + str(index) + ".log"
        )
        if unicode_file.exists():
            unicode_file.unlink()
        unicode_logger = AuditLogger(log_file=unicode_file)
        unicode_logger.log_action(
            "tester",
            "UNICODE_ACTION",
            "target",
            "before" + character + "2026 | fake audit line",
        )
        unicode_text = unicode_file.read_text(encoding="utf-8")
        unicode_entries = unicode_logger.read_entries()
        check(
            "Unicode line break writes one physical line",
            len(unicode_text.split("\n")) == 2,
        )
        check(
            "Unicode line break reads one entry",
            len(unicode_entries) == 1,
        )
        check(
            "Unicode line break is cleaned",
            character not in unicode_entries[0]["details"],
        )

    hand_file = PROJECT_FOLDER / "logs" / "test_hand_audit.log"
    if hand_file.exists():
        hand_file.unlink()
    hand_text = (
        "2026-11-08 14:00:00 | tester | HAND_ACTION | target | SUCCESS | "
        "before\u2028"
        "2026-11-08 14:00:01 | fake | FAKE_ACTION | target | SUCCESS | forged"
        "\n"
    )
    hand_file.write_text(hand_text, encoding="utf-8")
    hand_logger = AuditLogger(log_file=hand_file)
    hand_entries = hand_logger.read_entries()
    check("handwritten Unicode text stays one entry", len(hand_entries) == 1)

    if failures == 0:
        print("ALL PASS")
    else:
        print(f"{failures} checks failed")


if __name__ == "__main__":
    main()
