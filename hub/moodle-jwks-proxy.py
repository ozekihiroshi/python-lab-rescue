#!/usr/bin/env python3
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


upstream_url = os.environ.get(
    "MOODLE_JWKS_UPSTREAM",
    "http://moodle-rescue-local/mod/lti/certs.php",
)
upstream_host = os.environ.get("MOODLE_CANONICAL_HOST", "localhost:8083")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {"/jwks", "/health"}:
            self.send_error(404)
            return
        try:
            request = urllib.request.Request(
                upstream_url,
                headers={"Host": upstream_host, "Accept": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = response.read()
            document = json.loads(payload)
            if not isinstance(document.get("keys"), list):
                raise ValueError("Moodle JWKS has no keys array")
        except Exception:
            self.send_error(502, "Moodle JWKS is unavailable")
            return

        if self.path == "/health":
            payload = b'{"status":"ok"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return


ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
