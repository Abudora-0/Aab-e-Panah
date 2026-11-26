import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "frontend" / "index.html"
FRONTEND = ROOT / "frontend"


def check_linked_files():
    html = INDEX.read_text(encoding="utf-8")
    links = re.findall(r'\bhref="([^"]+)"', html)
    scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
    images = re.findall(r'<img[^>]+src="([^"]+)"', html)
    css_paths = []
    for css_file in (FRONTEND / "css").glob("*.css"):
        css_text = css_file.read_text(encoding="utf-8")
        css_paths.extend(re.findall(r'url\(["\']?([^"\')]+)', css_text))
    paths = links + scripts + images + css_paths
    missing = []
    for path in paths:
        if path.startswith("#"):
            continue
        path = path.split("#", 1)[0]
        if path.startswith("/static/"):
            relative_path = path.removeprefix("/static/")
        elif path.startswith("/"):
            relative_path = path.removeprefix("/")
        else:
            relative_path = path
        if not (FRONTEND / relative_path).exists():
            missing.append(path)
    return not missing


def check_no_external_links():
    html = INDEX.read_text(encoding="utf-8")
    return not re.search(r'\b(?:href|src)="https?://', html, re.IGNORECASE)


def check_vendor_files():
    expected_files = [
        "vendor/gsap/gsap.min.js",
        "vendor/gsap/ScrollTrigger.min.js",
        "vendor/lucide/sprite.svg",
        "vendor/lucide/LICENSE",
        "vendor/fonts/bricolage-grotesque-latin-400-normal.woff2",
        "vendor/fonts/instrument-sans-latin-400-normal.woff2",
        "vendor/fonts/jetbrains-mono-latin-400-normal.woff2",
        "vendor/fonts/bricolage-grotesque-LICENSE",
        "vendor/fonts/instrument-sans-LICENSE",
        "vendor/fonts/jetbrains-mono-LICENSE",
        "vendor/THIRD_PARTY.md",
    ]
    return all((FRONTEND / path).is_file() for path in expected_files)


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
        content = script.read_text(encoding="utf-8")
        if any(
            unsafe_api in content
            for unsafe_api in ("innerHTML", "outerHTML", "insertAdjacentHTML")
        ):
            return False
    return True


def check_motion_and_focus_rules():
    css = ""
    for css_file in (FRONTEND / "css").glob("*.css"):
        css += css_file.read_text(encoding="utf-8")
    has_reduced_motion = re.search(
        r"@media\s*\(prefers-reduced-motion:\s*reduce\)",
        css,
    )
    has_focus_visible = ":focus-visible" in css
    return has_reduced_motion is not None and has_focus_visible


def run_checks():
    checks = [
        check_linked_files(),
        check_no_external_links(),
        check_vendor_files(),
        check_script_ids(),
        check_no_inner_html(),
        check_image_alt_text(),
        check_no_placeholder_logos(),
        check_empty_camps_message(),
        check_motion_and_focus_rules(),
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
