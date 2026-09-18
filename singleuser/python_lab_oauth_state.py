"""Use a distinct OAuth state cookie for every single-user login attempt.

JupyterHub 5.5.0 only adds a random cookie-name suffix when the request
already contains the base state cookie. Two initial requests that arrive
before either response is stored can therefore overwrite each other. The
callback already reads the cookie name from the server-side state record, so
always assigning a unique name preserves the normal state validation while
removing that initial-name collision.
"""

import os
import secrets
from urllib.parse import urlparse

from jupyterhub.services.auth import HubOAuth
from jupyterhub.utils import get_browser_protocol


def _set_unique_state_cookie(self, handler, next_url=None):
    cookie_name = f"{self.state_cookie_name}-{secrets.token_hex(8)}"
    state_id = self.generate_state(next_url, cookie_name=cookie_name)
    options = {
        "path": self.cookie_path,
        "httponly": True,
        "max_age": 600,
    }

    public_url = os.getenv("JUPYTERHUB_PUBLIC_URL")
    if public_url:
        if urlparse(public_url).scheme == "https":
            options["secure"] = True
    elif get_browser_protocol(handler.request) == "https":
        options["secure"] = True

    protected = set(options) | {"expires_days", "expires"}
    for key, value in self.cookie_options.items():
        if key.lower() not in protected:
            options[key] = value

    handler.set_secure_cookie(cookie_name, state_id, **options)
    return state_id


_set_unique_state_cookie.python_lab_unique_state_cookies = True
HubOAuth.set_state_cookie = _set_unique_state_cookie
