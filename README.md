# Python Lab Rescue

A reproducible, server-saved Python learning environment for Moodle courses.
This repository is intentionally separate from `moodle-rescue`: Moodle owns
learning content, quizzes, assignments, and grades; Python Lab owns code
execution and learners' live notebook workspaces.

## Current scope

The current stage is local-only and runs with the Docker Engine inside WSL.
It does not use Docker Desktop, the existing Traefik deployment, or S3. It
supports direct development login and Moodle LTI 1.3 login.

It provides:

- JupyterHub 5.5.0
- DockerSpawner 14.0.0
- A dated Jupyter minimal-notebook base image with only course-required packages
- pandas, matplotlib, openpyxl, and the standard scientific Python stack
- One disposable container and one persistent named volume per learner
- A starter notebook and fictional learning-centre CSV
- CPU, memory, process, capability, and network restrictions

## Start in WSL

From Ubuntu 24.04 in WSL:

```sh
cd /mnt/d/workspace/python-lab-rescue
cp .env.example .env
```

Edit `.env` and replace `LAB_LOCAL_PASSWORD` with at least 16 characters. Then:

```sh
sh scripts/start-local.sh
```

Open <http://127.0.0.1:8086>. For this local phase, any test username may be
used with the configured local password. The username `admin` receives Hub
administrator privileges by default. A general launch opens
`00_start_here.ipynb`; learners should use the notebook rather than choosing a
Console from the JupyterLab Launcher.

This authentication mode is deliberately rejected unless
`LAB_LOCAL_DEVELOPMENT=true`. It must never be exposed through Traefik or a
public interface.

## Moodle LTI 1.3 mode

The reproducible Moodle registration is owned by `moodle-rescue`. Its
`scripts/configure-python-lab-lti.php` creates the site tool and adds the
`Python Lab` activity to `PYAI-INTRO`.

`scripts/configure-python-lab-notebooks.php` then adds 12 lesson activities and
five project activities. Each LTI launch opens its exact notebook rather than
the JupyterLab file browser. The notebooks use one connected learning-centre
story from basic output through CSV cleaning, visualisation, and chunked
processing.

The local browser-visible endpoints are:

- Moodle issuer: `http://localhost:8083`
- Tool target: `http://localhost:8086/hub/`
- OIDC login: `http://localhost:8086/hub/lti13/oauth_login`
- OAuth callback: `http://localhost:8086/hub/lti13/oauth_callback`

Set `LAB_AUTH_MODE=lti13` and fill the generated Client ID and Moodle
endpoints in `.env`. Direct Hub password login is then unavailable; launch
Python Lab from Moodle. The fixed-purpose `moodle-jwks-proxy` lets the Hub
validate Moodle signatures without publishing Moodle beyond
`127.0.0.1:8083`. Only the Hub and proxy share their private service network;
learner containers cannot reach the Moodle network.

Course-material releases use a versioned startup marker and merge missing
files recursively, including files added later inside an existing `data/`
directory. Existing learner files are never overwritten, while course copies
remain writable so notebooks can be edited and saved in the learner volume.

## Verify persistence

```sh
sh scripts/verify-local.sh
```

The verification checks the Compose model, Hub dependencies and health, then
writes a marker through one container and reads it through a replacement
container attached to the same named volume. It also simulates an older learner
volume and verifies that nested data files are added, learner edits survive,
and course notebooks remain writable. In `local` authentication mode it
also exercises direct login, spawn, package imports, stop, respawn, and
persistence. In `lti13` mode it verifies Moodle JWKS reachability and the
public LTI configuration endpoint. The Moodle repository contains the
end-to-end signed launch test.

To verify through the UI, open `00_start_here.ipynb`, change `learner_name`,
save, sign out, and sign in again with the same username. DockerSpawner removes
the stopped learner container while retaining `python-lab-user-<username>`.

## Stop without deleting work

```sh
sh scripts/stop-local.sh
```

Do not run `docker compose down -v`: `-v` deletes Hub state. Learner volumes
are dynamically created outside the Compose volume list, but they are also
material data and must be removed only by an explicit, verified operation.

## Next stages

The local LTI 1.3 launch and topic-specific notebook links are implemented.
Two Moodle learners tested from the same client receive separate named volumes;
new course materials are added without replacing their saved work. The final
infrastructure stage moves shared Traefik ownership out of `demand-monitor`
and publishes Moodle and Python Lab as separate HTTPS services. See
`docs/architecture.md`, `docs/production-with-traefik-rescue.md`, and
`SECURITY.md` before deployment. The production override and verification
script support an invite-only same-host pilot; a wider service should isolate
Python Lab on a dedicated host.

## License

The Docker, JupyterHub, integration, verification, and executable source code
in this repository is licensed under GNU GPL version 3 or, at your option, any
later version (`GPL-3.0-or-later`). See [LICENSE](LICENSE).

The original learner-facing course materials under `course-materials/` are
licensed under Creative Commons Attribution 4.0 International (`CC BY 4.0`).
See [CONTENT-LICENSE.txt](CONTENT-LICENSE.txt) for attribution and scope.
Bundled third-party software and base images retain their own licenses.
