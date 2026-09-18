"""Check installed HubOAuth cookie naming without requests or credentials.

This reproduces cookie-name selection only, not an end-to-end browser login.
No state values, cookies, tokens, or environment values are printed.
"""
import json
from importlib.metadata import version
from types import SimpleNamespace
from jupyterhub.services.auth import HubOAuth


class Handler:
    def __init__(self, cookies=None, protocol="http"):
        self.cookies = dict(cookies or {})
        self.writes = {}
        self.request = SimpleNamespace(protocol=protocol, headers={})

    def get_cookie(self, name):
        return self.cookies.get(name)

    def set_secure_cookie(self, name, value, **options):
        self.writes[name] = (value, options)


auth = HubOAuth(api_token="diagnostic-only-not-a-real-token", base_url="/diagnostic/")
patch_active = bool(getattr(
    HubOAuth.set_state_cookie, "python_lab_unique_state_cookies", False
))
assert patch_active, "Unique state-cookie patch is not active"
auth.cookie_options = {"samesite": "Lax"}

# Leave the first group unconsumed, like cancelled or interrupted logins, then
# create more requests carrying both base and suffixed stale cookies. Every
# request also uses a distinct destination to verify state metadata isolation.
handlers = []
states = []
names = []
for index in range(64):
    cookies = {}
    if index >= 16:
        cookies = {
            auth.state_cookie_name: "synthetic-stale-base-cookie",
            f"{auth.state_cookie_name}-stale": "synthetic-stale-suffix-cookie",
        }
    handler = Handler(cookies)
    next_url = f"/diagnostic/lab/workspace-{index}"
    state = auth.set_state_cookie(handler, next_url=next_url)
    name = auth.get_state_cookie_name(state)
    assert auth.get_next_url(state) == next_url
    assert list(handler.writes) == [name]
    handlers.append(handler)
    states.append(state)
    names.append(name)

assert len(set(states)) == len(states)
assert len(set(names)) == len(names)
assert all(name.startswith(f"{auth.state_cookie_name}-") for name in names)

https_handler = Handler(protocol="https")
https_state = auth.set_state_cookie(
    https_handler, next_url="/diagnostic/secure-destination"
)
https_name = auth.get_state_cookie_name(https_state)
assert https_name not in names
assert auth.get_next_url(https_state) == "/diagnostic/secure-destination"

for handler in [*handlers, https_handler]:
    for _, options in handler.writes.values():
        assert options["httponly"] is True
        assert options["max_age"] == 600
        assert options["path"] == auth.cookie_path
        assert options["samesite"] == "Lax"
assert next(iter(https_handler.writes.values()))[1]["secure"] is True

print(json.dumps({
    "jupyterhub": version("jupyterhub"),
    "unique_cookie_patch_active": patch_active,
    "request_count": len(states) + 1,
    "all_state_ids_distinct": True,
    "all_cookie_names_distinct": True,
    "cancelled_and_stale_cookie_followups": "PASS",
    "distinct_redirects_preserved": True,
    "httponly_expiry_path_and_samesite_preserved": True,
    "https_secure_cookie_preserved": True,
    "scope": "installed cookie-generation logic; no network or browser authentication",
}, indent=2))
