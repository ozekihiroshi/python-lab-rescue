# Production with Traefik Rescue

The Python course assumes a server-saved Python Lab. For an invite-only pilot,
Python Lab can run on the same Linux Docker host as Moodle and Traefik Rescue.
Traefik terminates HTTPS and is the only service that publishes ports 80 and
443. JupyterHub is reachable only through the shared `rescue_proxy` network.

This topology is not the final trust boundary for a broad public service.
JupyterHub controls Docker to create learner containers, so a larger deployment
should move Python Lab to a dedicated host while keeping the same public HTTPS
and LTI endpoints.

## Prepare

Start Traefik Rescue first so the external network exists. Then, in WSL or on
the Linux server:

```sh
cd /mnt/d/workspace/python-lab-rescue
cp .env.production.example .env.production
```

Set the public Moodle and Lab hostnames, Moodle LTI Client ID, and public HTTPS
Moodle endpoints. Do not use `docker-compose.lti.yml`; its JWKS proxy exists
only for the loopback local-development topology.

Validate without starting containers:

```sh
sh scripts/verify-production.sh
```

Start or update Python Lab:

```sh
sh scripts/start-production.sh
```

The production override removes the local `127.0.0.1:8086` publication,
connects only the Hub to `rescue_proxy`, and requires the two explicit gateway
labels. Learner containers remain on the internal Lab network.

## Operational checks

Before learners enter the service, verify the HTTPS certificate, Moodle LTI
launch, one learner spawn, save and respawn persistence, resource limits, Hub
backup, and a restore rehearsal. Never use `docker compose down -v` as an
ordinary stop operation.
