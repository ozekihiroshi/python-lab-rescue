import os


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def enabled(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


c = get_config()  # noqa: F821 - provided by JupyterHub.

c.JupyterHub.bind_url = "http://0.0.0.0:8000"
c.JupyterHub.hub_bind_url = "http://0.0.0.0:8081"
c.JupyterHub.hub_connect_url = "http://jupyterhub:8081"
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/data/jupyterhub.sqlite"
c.JupyterHub.log_level = os.environ.get("LAB_LOG_LEVEL", "INFO")

authmode = os.environ.get("LAB_AUTH_MODE", "local").strip().lower()
c.Authenticator.allow_all = True
c.Authenticator.admin_users = {
    username.strip()
    for username in os.environ.get("LAB_ADMIN_USERS", "admin").split(",")
    if username.strip()
}

if authmode == "local":
    if not enabled("LAB_LOCAL_DEVELOPMENT"):
        raise RuntimeError("Local authentication requires LAB_LOCAL_DEVELOPMENT=true")
    password = required("LAB_LOCAL_PASSWORD")
    if password.startswith("CHANGE_ME") or len(password) < 16:
        raise RuntimeError("LAB_LOCAL_PASSWORD must be changed and contain at least 16 characters")
    c.JupyterHub.authenticator_class = "jupyterhub.auth.DummyAuthenticator"
    c.DummyAuthenticator.password = password
elif authmode == "lti13":
    uri_scheme = os.environ.get("LTI13_URI_SCHEME", "auto").strip().lower() or "auto"
    if uri_scheme == "http" and not enabled("LAB_LOCAL_DEVELOPMENT"):
        raise RuntimeError("HTTP LTI is permitted only with LAB_LOCAL_DEVELOPMENT=true")
    c.JupyterHub.authenticator_class = "ltiauthenticator.lti13.auth.LTI13Authenticator"
    c.LTI13Authenticator.issuer = required("LTI13_ISSUER")
    c.LTI13Authenticator.client_id = [
        value.strip() for value in required("LTI13_CLIENT_ID").split(",") if value.strip()
    ]
    c.LTI13Authenticator.authorize_url = required("LTI13_AUTHORIZE_URL")
    c.LTI13Authenticator.jwks_endpoint = required("LTI13_JWKS_ENDPOINT")
    c.LTI13Authenticator.username_key = os.environ.get("LTI13_USERNAME_KEY", "sub").strip() or "sub"
    c.LTI13Authenticator.uri_scheme = uri_scheme
    c.LTI13Authenticator.tool_name = "Python Lab"
    c.LTI13Authenticator.tool_description = (
        "Server-saved JupyterLab workspace for the Python for Data course"
    )
else:
    raise RuntimeError(f"Unsupported LAB_AUTH_MODE: {authmode}")

c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = required("LAB_SINGLEUSER_IMAGE")
c.DockerSpawner.cmd = ["start-singleuser.py"]
c.DockerSpawner.name_template = "python-lab-{username}"
c.DockerSpawner.network_name = required("LAB_DOCKER_NETWORK")
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.notebook_dir = "/home/jovyan/work"
c.DockerSpawner.volumes = {
    f"{os.environ.get('LAB_USER_VOLUME_PREFIX', 'python-lab-user')}-{{username}}": "/home/jovyan/work"
}
c.DockerSpawner.remove = True
c.DockerSpawner.extra_host_config = {
    "cap_drop": ["ALL"],
    "security_opt": ["no-new-privileges"],
    "pids_limit": int(os.environ.get("LAB_PIDS_LIMIT", "256")),
}

c.Spawner.default_url = "/lab/tree/00_start_here.ipynb"
c.Spawner.mem_limit = os.environ.get("LAB_MEM_LIMIT", "1G")
c.Spawner.cpu_limit = float(os.environ.get("LAB_CPU_LIMIT", "1.0"))
c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 60

c.JupyterHub.shutdown_on_logout = False
c.JupyterHub.cleanup_servers = True

c.JupyterHub.services = [
    {
        "name": "moodle-submit",
        "command": ["python", "/srv/jupyterhub/moodle-submit-service.py"],
        "url": "http://127.0.0.1:8090",
    }
]

c.Spawner.environment = {
    "PYTHON_LAB_SUBMIT_URL": "http://jupyterhub:8090/api/submit",
}
