#!/usr/bin/env python3
"""Generate the canonical-host-aware submission service variant."""
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "hub/moodle-submit-service.py"
target = source.with_name("moodle-submit-service-v2.py")
text = source.read_text(encoding="utf-8")
needle = '''            headers={
                "Content-Type": "application/json",
                "X-Python-Lab-Timestamp": timestamp,'''
replacement = '''            headers={
                "Content-Type": "application/json",
                "Host": os.environ.get("PYTHON_LAB_MOODLE_CANONICAL_HOST", "localhost:8083"),
                "X-Python-Lab-Timestamp": timestamp,'''
if needle not in text:
    raise RuntimeError("Upstream request header block not found")
target.write_text(text.replace(needle, replacement), encoding="utf-8")
print(target)
