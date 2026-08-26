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
compose="docker compose --env-file .env $compose_files"
$compose config --quiet
$compose exec -T jupyterhub python -c "import dockerspawner, ltiauthenticator; print('hub dependencies: ok')"

python3 - "$LAB_PORT" <<'PY'
import sys
import urllib.request

with urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[1]}/hub/health", timeout=5) as response:
    if response.status != 200:
        raise SystemExit(f"unexpected health status: {response.status}")
print("hub health: ok")
PY

test_volume="python-lab-rescue-persistence-test"
trap 'docker volume rm -f "$test_volume" >/dev/null 2>&1 || true' EXIT
docker volume create "$test_volume" >/dev/null
docker run --rm --entrypoint sh \
    -v "$test_volume:/home/jovyan/work" \
    "$LAB_SINGLEUSER_IMAGE" \
    -c 'printf "%s\n" "server-persistence-ok" > /home/jovyan/work/persistence.txt'
docker run --rm --entrypoint sh \
    -v "$test_volume:/home/jovyan/work" \
    "$LAB_SINGLEUSER_IMAGE" \
    -c 'test "$(cat /home/jovyan/work/persistence.txt)" = "server-persistence-ok"'

# Reproduce an existing learner volume whose data directory and notebook predate a course release.
docker run --rm --entrypoint sh \
    -v "$test_volume:/home/jovyan/work" \
    "$LAB_SINGLEUSER_IMAGE" \
    -c 'mkdir -p /home/jovyan/work/data; printf "%s\n" "learner-edit" > /home/jovyan/work/07_tables_csv_pandas.ipynb; printf "%s\n" "keep-me" > /home/jovyan/work/data/learner-note.txt'
docker run --rm --entrypoint sh \
    -v "$test_volume:/home/jovyan/work" \
    "$LAB_SINGLEUSER_IMAGE" \
    /usr/local/bin/start-notebook.d/10-python-lab-materials.sh
docker run --rm --entrypoint sh \
    -v "$test_volume:/home/jovyan/work" \
    "$LAB_SINGLEUSER_IMAGE" \
    -c 'test "$(cat /home/jovyan/work/07_tables_csv_pandas.ipynb)" = "learner-edit"; test "$(cat /home/jovyan/work/data/learner-note.txt)" = "keep-me"; test -f /home/jovyan/work/data/learning-centres-practice.csv; test -f /home/jovyan/work/data/generate-learning-centre-data.py; test -w /home/jovyan/work/07_tables_csv_pandas.ipynb'


# Exercise the image's real start script. start-notebook.d hooks are sourced,
# so shell options set by a hook can otherwise break the parent startup later.
docker run --rm \
    -v "$test_volume:/home/jovyan/work" \
    "$LAB_SINGLEUSER_IMAGE" \
    python -c 'from pathlib import Path; assert Path("/home/jovyan/work/00_start_here.ipynb").is_file()'

echo "single-user entrypoint, volume persistence, and course-material merge: ok"
case "${LAB_AUTH_MODE:-local}" in
    local)
        python3 scripts/smoke-user-flow.py
        ;;
    lti13)
        $compose exec -T jupyterhub python -c \
            "import json, os, urllib.request; json.load(urllib.request.urlopen(os.environ['LTI13_JWKS_ENDPOINT'], timeout=10)); print('Moodle JWKS reachability: ok')"
        python3 scripts/verify-lti-config.py
        ;;
    *)
        echo "Unsupported LAB_AUTH_MODE: ${LAB_AUTH_MODE}" >&2
        exit 1
        ;;
esac
