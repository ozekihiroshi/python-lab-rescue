#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

env_file=${LAB_ENV_FILE:-.env.production}
if [ ! -f "$env_file" ]; then
    env_file=.env.production.example
fi

docker compose --env-file "$env_file" -f docker-compose.local.yml -f docker-compose.production.yml config --quiet
docker compose --env-file "$env_file" -f docker-compose.local.yml -f docker-compose.production.yml config --format json | python3 -c '
import json
import sys

service = json.load(sys.stdin)["services"]["jupyterhub"]
assert service.get("ports", []) == [], "production must not publish the Hub port"
labels = service.get("labels", {})
if isinstance(labels, list):
    labels = dict(item.split("=", 1) for item in labels)
assert labels.get("traefik.enable") == "true"
assert labels.get("traefik.rescue.gateway") == "true"
assert labels.get("traefik.http.services.python-lab.loadbalancer.server.port") == "8000"
networks = set(service.get("networks", {}))
assert networks == {"lab_internal", "proxy"}, f"unexpected Hub networks: {sorted(networks)}"
environment = service.get("environment", {})
assert environment.get("LAB_AUTH_MODE") == "lti13"
assert environment.get("LAB_LOCAL_DEVELOPMENT") == "false"
assert environment.get("LTI13_URI_SCHEME") == "https"
assert str(environment.get("LTI13_JWKS_ENDPOINT", "")).startswith("https://")
'

echo "Python Lab production Compose invariants verified."
