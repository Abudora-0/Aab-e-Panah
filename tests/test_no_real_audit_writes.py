# This test checks that test runs do not change the real audit log.

import subprocess
import sys
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from backend.database.db_connection import test_connection

REAL_LOG = PROJECT_FOLDER / "logs" / "audit.log"


def line_count(path):
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def run_test(path):
    result = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    output_lines = output.splitlines()
    passed = "ALL PASS" in output_lines or "PASS" in output_lines
    for line in output_lines:
        if line.startswith("FAIL:") or "checks failed" in line:
            passed = False
    if result.returncode != 0:
        passed = False
    return passed


def main():
    failures = 0
    before = line_count(REAL_LOG)
    test_names = [
        "test_structures.py",
        "test_algorithms.py",
        "test_api_validation.py",
        "test_audit_viewer.py",
        "test_logging.py",
    ]

    if test_connection():
        test_names.extend(
            [
                "test_requests_db.py",
                "test_supplies.py",
                "test_occupancy.py",
            ]
        )

    for test_name in test_names:
        path = PROJECT_FOLDER / "tests" / test_name
        if run_test(path):
            print("PASS:", test_name)
        else:
            print("FAIL:", test_name)
            failures += 1

    after = line_count(REAL_LOG)
    if after == before:
        print("PASS: real audit log unchanged")
    else:
        print("FAIL: real audit log changed")
        failures += 1

    if failures == 0:
        print("ALL PASS")
    else:
        print(str(failures) + " checks failed")


if __name__ == "__main__":
    main()
