"""Validate that the self-contained browser console has parsable JavaScript."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest


def test_inline_javascript_parses(tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js not installed")
    html = (Path(__file__).parents[1] / "web" / "index.html").read_text()
    match = re.search(r"<script>([\s\S]*?)</script>", html)
    assert match, "Expected inline browser script"
    js = tmp_path / "console.js"
    js.write_text(match.group(1))
    result = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_browser_console_is_honest_about_demo_mode():
    html = (Path(__file__).parents[1] / "web" / "index.html").read_text()
    assert "LOCAL_BROWSER_ONLY" in html
    assert "audit_signed: false" in html
    assert "Air-Gapped Active" not in html
