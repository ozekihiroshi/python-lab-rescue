#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

if [ ! -f .env ]; then
    echo "Missing .env. Copy .env.example to .env and change LAB_LOCAL_PASSWORD." >&2
    exit 1
fi

set -a
. ./.env
set +a

compose_files="-f docker-compose.local.yml"
if [ "${LAB_AUTH_MODE:-local}" = "lti13" ]; then
    compose_files="$compose_files -f docker-compose.lti.yml"
fi
compose="docker compose --env-file .env $compose_files"

$compose --profile build build
$compose up -d jupyterhub

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

port=$(sed -n 's/^LAB_PORT=//p' .env | tail -n 1)
echo "Python Lab is ready at http://127.0.0.1:${port:-8086}"
