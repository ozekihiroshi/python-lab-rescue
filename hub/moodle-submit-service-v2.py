"""Authenticated bridge from a learner server to Moodle Assignment."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


MAX_BODY = 400_000


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


HUB_API_URL = required("JUPYTERHUB_API_URL").rstrip("/")
MOODLE_SUBMIT_URL = required("PYTHON_LAB_MOODLE_SUBMIT_URL")
SUBMIT_SECRET = required("PYTHON_LAB_SUBMIT_SECRET")
if len(SUBMIT_SECRET) < 32 or SUBMIT_SECRET.startswith("CHANGE_ME"):
    raise RuntimeError("PYTHON_LAB_SUBMIT_SECRET must contain at least 32 random characters")


class Handler(BaseHTTPRequestHandler):
    server_version = "PythonLabSubmit/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"moodle-submit: {self.address_string()} {fmt % args}", flush=True)

    def send_json(self, status: int, data: dict[str, object]) -> None:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(200, {"ok": True})
            return
        self.send_json(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/api/submit":
            self.send_json(404, {"ok": False, "error": "not_found"})
            return

        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("token "):
            self.send_json(401, {"ok": False, "error": "missing_hub_token"})
            return
        token = authorization.removeprefix("token ").strip()

        try:
            user_request = urllib.request.Request(
                f"{HUB_API_URL}/user",
                headers={"Authorization": f"token {token}"},
            )
            with urllib.request.urlopen(user_request, timeout=5) as response:
                hub_user = json.load(response)
        except (urllib.error.URLError, json.JSONDecodeError):
            self.send_json(401, {"ok": False, "error": "invalid_hub_token"})
            return

        username = str(hub_user.get("name", ""))
        if not username.isdigit() or int(username) <= 0:
            self.send_json(403, {"ok": False, "error": "not_an_lti_learner"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self.send_json(413, {"ok": False, "error": "request_too_large"})
            return
        raw = self.rfile.read(length)
        try:
            request_data = json.loads(raw)
        except json.JSONDecodeError:
            self.send_json(400, {"ok": False, "error": "invalid_json"})
            return

        upstream_data = {
            "userid": int(username),
            "course_shortname": request_data.get("course_shortname"),
            "project": request_data.get("project"),
            "filename": request_data.get("filename"),
            "content_base64": request_data.get("content_base64"),
            "sha256": request_data.get("sha256"),
        }
        upstream_body = json.dumps(
            upstream_data, ensure_ascii=False, separators=(",", ":")
        ).encode()
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        digest = hmac.new(
            SUBMIT_SECRET.encode(),
            timestamp.encode() + b"\n" + nonce.encode() + b"\n" + upstream_body,
            hashlib.sha256,
        ).hexdigest()
        upstream_headers = {
            "Content-Type": "application/json",
            "X-Python-Lab-Timestamp": timestamp,
            "X-Python-Lab-Nonce": nonce,
            "X-Python-Lab-Signature": f"sha256={digest}",
        }
        canonicalhost = os.environ.get("PYTHON_LAB_MOODLE_CANONICAL_HOST", "").strip()
        if canonicalhost:
            upstream_headers["Host"] = canonicalhost
        upstream_request = urllib.request.Request(
            MOODLE_SUBMIT_URL,
            data=upstream_body,
            method="POST",
            headers=upstream_headers,
        )
        try:
            with urllib.request.urlopen(upstream_request, timeout=20) as response:
                result = json.load(response)
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
            try:
                result = json.load(error)
            except json.JSONDecodeError:
                result = {"ok": False, "error": "moodle_request_failed"}
        except (urllib.error.URLError, TimeoutError):
            self.send_json(502, {"ok": False, "error": "moodle_unavailable"})
            return

        self.send_json(status, result)


if __name__ == "__main__":
    port = int(os.environ.get("PYTHON_LAB_SUBMIT_PORT", "8090"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
