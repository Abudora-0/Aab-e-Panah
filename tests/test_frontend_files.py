import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "frontend" / "index.html"
FRONTEND = ROOT / "frontend"


def check_linked_files():
    html = INDEX.read_text(encoding="utf-8")
    links = re.findall(r'<link[^>]+href="([^"]+)"', html)
    scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
    paths = links + scripts
    missing = []
    for path in paths:
        relative_path = path.removeprefix("/static/")
        if not (FRONTEND / relative_path).exists():
            missing.append(path)
    return not missing


def check_script_ids():
    html = INDEX.read_text(encoding="utf-8")
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    script_ids = set()
    for script in (FRONTEND / "js").glob("*.js"):
        content = script.read_text(encoding="utf-8")
        script_ids.update(re.findall(r'getElementById\("([^"]+)"\)', content))
    return script_ids.issubset(ids)


def check_no_inner_html():
    for script in (FRONTEND / "js").glob("*.js"):
        if "innerHTML" in script.read_text(encoding="utf-8"):
            return False
    return True


def run_checks():
    checks = [
        check_linked_files(),
        check_script_ids(),
        check_no_inner_html(),
    ]
    return len([check for check in checks if not check])


def test_frontend_files():
    failed = run_checks()
    if failed == 0:
        print("ALL PASS")
    else:
        print(str(failed) + " failed checks")
    assert failed == 0


if __name__ == "__main__":
    failed = run_checks()
    if failed == 0:
        print("ALL PASS")
    else:
        print(str(failed) + " failed checks")
    raise SystemExit(failed)
