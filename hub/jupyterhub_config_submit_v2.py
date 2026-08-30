"""Base JupyterHub configuration plus the Moodle submission service."""
import os
exec(compile(open('/srv/jupyterhub/jupyterhub_config.py', encoding='utf-8').read(),
             '/srv/jupyterhub/jupyterhub_config.py', 'exec'))
c.JupyterHub.services = [  # noqa: F821
    {
        "name": "moodle-submit",
        "command": ["python", "/srv/jupyterhub/moodle-submit-service-v2.py"],
        "url": "http://127.0.0.1:8090",
        "environment": {
            "PYTHON_LAB_MOODLE_SUBMIT_URL": os.environ["PYTHON_LAB_MOODLE_SUBMIT_URL"],
            "PYTHON_LAB_MOODLE_CANONICAL_HOST": os.environ.get("PYTHON_LAB_MOODLE_CANONICAL_HOST", "localhost:8083"),
            "PYTHON_LAB_SUBMIT_SECRET": os.environ["PYTHON_LAB_SUBMIT_SECRET"],
        },
    }
]
c.Spawner.environment = {  # noqa: F821
    "PYTHON_LAB_SUBMIT_URL": "http://jupyterhub:8090/api/submit",
}
