#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

if [ ! -f .env ]; then
    echo "Missing .env. Copy .env.example to .env and configure the local LTI settings." >&2
    exit 1
fi

# The repository is also operated from Windows, where .env may use CRLF.
# Source a private normalized copy without changing or printing its secrets.
env_file=$(mktemp)
trap 'rm -f "$env_file"' EXIT HUP INT TERM
tr -d '\r' < .env > "$env_file"
set -a
. "$env_file"
set +a

if [ "${LAB_AUTH_MODE:-}" != "lti13" ]; then
    echo "LAB_AUTH_MODE must be lti13 for this start command." >&2
    exit 1
fi

compose="docker compose --env-file .env -f docker-compose.local.yml -f docker-compose.lti.yml -f docker-compose.submit-v4.yml"

# Build both the dated learner image and the distinct submission-enabled Hub
# image before startup. This prevents a same-tag base Hub image being reused.
$compose --profile build build singleuser-image jupyterhub
$compose up -d moodle-jwks-proxy jupyterhub

attempt=0
until [ "$(docker inspect --format '{{.State.Health.Status}}' python-lab-rescue-jupyterhub-1 2>/dev/null || true)" = "healthy" ]; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 60 ]; then
        $compose logs --tail=100 jupyterhub
        echo "JupyterHub did not become healthy." >&2
        exit 1
    fi
    sleep 2
done

port=$(sed -n 's/^LAB_PORT=//p' "$env_file" | tail -n 1)
echo "Python Lab LTI is ready at http://127.0.0.1:${port:-8086}"
