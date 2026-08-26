#!/usr/bin/env python3
import json
import os
import urllib.request


port = os.environ.get("LAB_PORT", "8086").strip()
base_url = f"http://127.0.0.1:{port}"

with urllib.request.urlopen(f"{base_url}/hub/lti13/config", timeout=10) as response:
    config = json.load(response)

expected_login = f"{base_url}/hub/lti13/oauth_login"
if config.get("title") != "Python Lab":
    raise RuntimeError(f"Unexpected LTI tool title: {config.get('title')!r}")
if config.get("oidc_initiation_url") != expected_login:
    raise RuntimeError(
        f"Unexpected OIDC initiation URL: {config.get('oidc_initiation_url')!r}"
    )
if config.get("target_link_uri") != base_url:
    raise RuntimeError(f"Unexpected target link URI: {config.get('target_link_uri')!r}")

print("LTI 1.3 configuration endpoint: ok")
