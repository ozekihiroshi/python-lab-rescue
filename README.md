# Python Lab Rescue

A reproducible, server-saved Python learning environment for Moodle courses.
This repository is intentionally separate from `moodle-rescue`: Moodle owns
learning content, quizzes, assignments, and grades; Python Lab owns code
execution and learners' live notebook workspaces.

## Status

This is an alpha release. Local development runs with the Docker Engine inside
WSL and does not require Docker Desktop. An invite-only pilot can use Moodle
LTI 1.3 over HTTPS through the separate Traefik Rescue gateway. The same-host
pilot is not the recommended trust boundary for a broad public service;
JupyterHub controls Docker to create learner containers, so larger deployments
should place Python Lab on a dedicated host.

It provides:

- JupyterHub 5.5.0
- DockerSpawner 14.0.0
- A dated Jupyter minimal-notebook base image with only course-required packages
- pandas, matplotlib, openpyxl, and the standard scientific Python stack
- One disposable container and one persistent named volume per learner
- Bilingual lesson notebooks, practical projects, fictional CSV data, and checks
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

`scripts/configure-python-lab-notebooks.php` registers the lesson and project
activities for the bundled course release. Each launch opens its exact notebook
rather than the JupyterLab file browser. The notebooks use one connected
learning-centre
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

## Invite-only HTTPS pilot

For a same-host pilot with Traefik Rescue, follow
[the production guide](docs/production-with-traefik-rescue.md). It removes the
loopback Hub port, requires HTTPS Moodle LTI endpoints, and does not use the
local JWKS proxy. Review [SECURITY.md](SECURITY.md) before exposing the service.

The Moodle course may be published for password-free guest reading, but Python
Lab is not an anonymous execution service. Learners must sign in to Moodle and
launch the Lab through LTI 1.3 so that each persistent workspace has a stable
owner. Do not publish the local DummyAuthenticator endpoint or give anonymous
guests a shared Lab identity.

The Moodle assignment submission bridge is optional. Set
`PYTHON_LAB_SUBMIT_ENABLED=true` only after configuring the matching secret and
HTTPS submission endpoint in `moodle-rescue`; otherwise learners can still save
their work in Python Lab and use the course's manual download/upload route.

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

## Alpha limitations

The local LTI launch, learner-volume separation, course-material updates, and
topic-specific notebook links have been exercised. The production override and
verification script support an invite-only same-host pilot through Traefik
Rescue. The following are not complete production guarantees:

- no high-availability Hub or multi-host scheduler;
- no bundled backup scheduler or automated restore rehearsal for learner volumes;
- no isolation of Docker control beyond the documented host boundary;
- no offline mode;
- no promise of preserving files deleted or replaced manually by a learner;
- no broad public deployment security review.

Read [the architecture stages](docs/architecture.md),
[the Traefik Rescue production guide](docs/production-with-traefik-rescue.md),
and [SECURITY.md](SECURITY.md) before deployment.

## License

The Docker, JupyterHub, integration, verification, and executable source code
in this repository is licensed under GNU GPL version 3 or, at your option, any
later version (`GPL-3.0-or-later`). See [LICENSE](LICENSE).

The original learner-facing course materials under `course-materials/` are
licensed under Creative Commons Attribution 4.0 International (`CC BY 4.0`).
See [CONTENT-LICENSE.txt](CONTENT-LICENSE.txt) for attribution and scope.
Bundled third-party software and base images retain their own licenses.
