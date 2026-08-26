#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

if [ ! -f .env ]; then
    echo "Missing .env." >&2
    exit 1
fi

set -a
. ./.env
set +a

compose_files="-f docker-compose.local.yml"
if [ "${LAB_AUTH_MODE:-local}" = "lti13" ]; then
    compose_files="$compose_files -f docker-compose.lti.yml"
fi

docker compose --env-file .env $compose_files stop
