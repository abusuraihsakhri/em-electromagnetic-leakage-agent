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


def test_local_evaluator_matches_python_worker_rules(tmp_path):
    """Run the browser's pure calculation under Node and exercise form handling."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js not installed")
    html = (Path(__file__).parents[1] / "web" / "index.html").read_text()
    match = re.search(r"<script>([\s\S]*?)</script>", html)
    assert match
    js = tmp_path / "console-rules.js"
    js.write_text(match.group(1) + """
const nominal = evaluateLocally({
    task_id: "T1", target_identifier: "KEY1",
    primary_metric: 15, secondary_metric: 2,
    status_descriptor: "NOMINAL", is_critical_flag: false
});
if (nominal.overall_urgency !== "ROUTINE" || nominal.total_alerts !== 0 ||
    nominal.audit_signed !== false || nominal.audit_hash !== null)
    throw new Error("Nominal browser evaluation mismatch");

const critical = evaluateLocally({
    task_id: "T2", target_identifier: "KEY2",
    primary_metric: 30, secondary_metric: 14,
    status_descriptor: "DISCORDANT", is_critical_flag: true
});
if (critical.overall_urgency !== "CRITICAL_STAT_PANIC" ||
    critical.total_alerts !== 3 || critical.critical_alerts_count !== 1)
    throw new Error("Critical browser evaluation mismatch");

const controls = {
    task_id: {value: "T3"},
    target_id: {value: "KEY3"},
    primary_metric: {value: "10"},
    secondary_metric: {value: "2"},
    status_descriptor: {value: "NOMINAL"},
    is_critical: {checked: false},
    outputConsole: {textContent: ""},
    downloadBtn: {disabled: true},
    "m-tasks": {textContent: "0"},
    "m-audit": {textContent: "0"},
    "m-status": {textContent: "READY"}
};
global.document = {getElementById: id => controls[id]};
runAudit();
if (!controls.outputConsole.textContent.includes('"mode": "LOCAL_BROWSER_ONLY"') ||
    controls.downloadBtn.disabled || controls["m-tasks"].textContent !== "1")
    throw new Error("Form dispatch failed");

controls.primary_metric.value = "";
runAudit();
if (!controls.downloadBtn.disabled || controls["m-tasks"].textContent !== "1")
    throw new Error("Invalid form should not create a result");
""")
    result = subprocess.run([node, str(js)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
