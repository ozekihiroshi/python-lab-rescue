#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

env_file=${LAB_ENV_FILE:-.env.production}
if [ ! -f "$env_file" ]; then
    echo "Missing $env_file. Copy .env.production.example and set the production values." >&2
    exit 1
fi

set -a
. "./$env_file"
set +a

[ "${LAB_AUTH_MODE:-}" = lti13 ] || {
    echo "Production requires LAB_AUTH_MODE=lti13." >&2
    exit 1
}
[ "${LAB_LOCAL_DEVELOPMENT:-}" = false ] || {
    echo "Production requires LAB_LOCAL_DEVELOPMENT=false." >&2
    exit 1
}

for value in LAB_HOST LTI13_ISSUER LTI13_CLIENT_ID LTI13_AUTHORIZE_URL LTI13_JWKS_ENDPOINT; do
    eval "current=\${$value:-}"
    [ -n "$current" ] || {
        echo "Missing required value: $value" >&2
        exit 1
    }
    case "$current" in
        *example.org*|*REPLACE*|*CHANGE_ME*)
            echo "Replace the example value for $value before production." >&2
            exit 1
            ;;
    esac
done

case "$LTI13_ISSUER $LTI13_AUTHORIZE_URL $LTI13_JWKS_ENDPOINT" in
    *http://*)
        echo "All production Moodle LTI endpoints must use HTTPS." >&2
        exit 1
        ;;
esac

network=${TRAEFIK_NETWORK:-rescue_proxy}
docker network inspect "$network" >/dev/null 2>&1 || {
    echo "Missing external Traefik network: $network" >&2
    echo "Start Traefik Rescue before Python Lab." >&2
    exit 1
}

compose="docker compose --env-file $env_file -f docker-compose.local.yml -f docker-compose.production.yml"
$compose --profile build build
$compose up -d jupyterhub

attempt=0
until [ "$(docker inspect --format '{{.State.Health.Status}}' python-lab-rescue-jupyterhub-1 2>/dev/null || true)" = healthy ]; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 60 ]; then
        $compose logs --tail=100 jupyterhub
        echo "JupyterHub did not become healthy." >&2
        exit 1
    fi
    sleep 2
done

echo "Python Lab is ready through https://${LAB_HOST}/"
