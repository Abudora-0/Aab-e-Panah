import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "frontend" / "index.html"
FRONTEND = ROOT / "frontend"


def check_linked_files():
    html = INDEX.read_text(encoding="utf-8")
    links = re.findall(r'<link[^>]+href="([^"]+)"', html)
    scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
    images = re.findall(r'<img[^>]+src="([^"]+)"', html)
    paths = links + scripts + images
    missing = []
    for path in paths:
        relative_path = path.removeprefix("/static/")
        if not (FRONTEND / relative_path).exists():
            missing.append(path)
    return not missing


def check_image_alt_text():
    html = INDEX.read_text(encoding="utf-8")
    images = re.findall(r"<img\b[^>]*>", html)
    for image in images:
        if not re.search(r'\balt="[^"]+"', image):
            return False
    return True


def check_no_placeholder_logos():
    html = INDEX.read_text(encoding="utf-8")
    return "logo.svg" not in html and "favicon.svg" not in html


def check_empty_camps_message():
    for script in (FRONTEND / "js").glob("*.js"):
        content = script.read_text(encoding="utf-8")
        start = 0
        while True:
            position = content.find("No camps are available", start)
            if position == -1:
                break
            context = content[max(0, position - 300):position + 300]
            if "length === 0" not in context:
                return False
            start = position + 1
    return True


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
        check_image_alt_text(),
        check_no_placeholder_logos(),
        check_empty_camps_message(),
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
