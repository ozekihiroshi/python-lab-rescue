#!/usr/bin/env python3
import http.cookiejar
import os
import re
import subprocess
import time
import urllib.parse
import urllib.error
import urllib.request


port = os.environ.get("LAB_PORT", "8086").strip()
password = os.environ["LAB_LOCAL_PASSWORD"].strip()
username = "smokelearner"
base_url = f"http://127.0.0.1:{port}"
container = f"python-lab-{username}"

cookies = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))


def xsrf_token() -> str:
    html = opener.open(f"{base_url}/hub/login", timeout=10).read().decode("utf-8")
    match = re.search(r'name="_xsrf" value="([^"]+)"', html)
    if not match:
        raise RuntimeError("JupyterHub login form did not contain an XSRF token")
    return match.group(1)


def container_running() -> bool:
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Running}}", container],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def wait_for_container(expected: bool, timeout: int = 180) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if container_running() is expected:
            return
        time.sleep(1)
    raise RuntimeError(f"Timed out waiting for learner container running={expected}")


def wait_for_user_server(timeout: int = 180) -> None:
    deadline = time.monotonic() + timeout
    last_url = ""
    while time.monotonic() < deadline:
        try:
            response = opener.open(f"{base_url}/user/{username}/", timeout=10)
            last_url = response.geturl()
            if last_url.endswith(
                f"/user/{username}/lab/tree/00_start_here.ipynb"
            ):
                return
        except urllib.error.HTTPError as error:
            last_url = f"HTTP {error.code}"
        time.sleep(1)
    raise RuntimeError(
        "Learner server did not open the start notebook: "
        f"{last_url}"
    )


def stop_server() -> None:
    xsrf = next((cookie.value for cookie in cookies if cookie.name == "_xsrf"), "")
    if not xsrf:
        raise RuntimeError("Authenticated XSRF cookie was not found")
    request = urllib.request.Request(
        f"{base_url}/hub/api/users/{username}/server",
        method="DELETE",
        headers={"X-XSRFToken": xsrf},
    )
    opener.open(request, timeout=30).read()


token = xsrf_token()
payload = urllib.parse.urlencode(
    {"_xsrf": token, "username": username, "password": password}
).encode("utf-8")
response = opener.open(
    urllib.request.Request(f"{base_url}/hub/login", data=payload), timeout=180
)
wait_for_container(True)
wait_for_user_server()

subprocess.run(
    [
        "docker",
        "exec",
        container,
        "python",
        "-c",
        (
            "import os, pathlib, pandas, matplotlib, openpyxl; "
            "root=pathlib.Path('/home/jovyan/work'); "
            "assert (root / '00_start_here.ipynb').is_file(); "
            "assert (root / 'data/learning-centres-practice.csv').is_file(); "
            "assert (root / 'data/generate-learning-centre-data.py').is_file(); "
            "assert os.access(root / '07_tables_csv_pandas.ipynb', os.W_OK); "
            "(root / '.server-persistence-smoke').write_text('ok')"
        ),
    ],
    check=True,
)

stop_server()
wait_for_container(False)

opener.open(f"{base_url}/hub/spawn", timeout=180)
wait_for_container(True)
wait_for_user_server()

subprocess.run(
    [
        "docker",
        "exec",
        container,
        "python",
        "-c",
        (
            "from pathlib import Path; "
            "assert Path('/home/jovyan/work/.server-persistence-smoke').read_text() == 'ok'"
        ),
    ],
    check=True,
)

stop_server()
wait_for_container(False)
print("authenticated spawn, course materials, package imports, and respawn persistence: ok")
