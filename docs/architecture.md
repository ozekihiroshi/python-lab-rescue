# Architecture stages

## Current local stage

- Independent `python-lab-rescue` Compose project
- WSL-hosted Docker Engine; Docker Desktop is not required
- JupyterHub published only on `127.0.0.1:8086`
- Direct local authentication or Moodle LTI 1.3 authentication
- DockerSpawner creates one disposable container per learner
- One named volume per learner stores notebooks on the server
- A dated minimal Jupyter image plus pinned pandas, matplotlib, and openpyxl
  versions avoids shipping the much larger general SciPy stack
- No dependency on the current shared Traefik deployment

The local completion gate is: the Hub is healthy, required extensions load,
the learner image runs, and a file written to a named volume remains readable
from a replacement container.

## Moodle integration stage

- `LAB_AUTH_MODE=lti13` and the LTIAuthenticator endpoints are implemented
- `moodle-rescue` owns the idempotent site-tool and course-activity registration
- The stable LTI `sub` claim is the learner workspace identifier
- A fixed-purpose local JWKS proxy preserves Moodle's loopback-only publication
- The proxy and Hub share a private service network; learner containers do not
  join the Moodle network
- Signed Moodle launch, Hub authentication, learner spawn, bundled materials,
  and package imports are verified
- Two Moodle learners tested from the same client receive distinct named
  volumes and recover only their own saved marker after reopening Python Lab
- Site-specific Client IDs and endpoints stay outside course `.mbz` backups

## Final shared-ingress stage

- Move Traefik and ACME state out of `demand-monitor` into a neutral edge project
- Create a neutral external network such as `traefik-public`
- Attach only the JupyterHub proxy-facing service to that network
- Keep learner containers on the private Python Lab network
- Publish Moodle and Python Lab on separate HTTPS hostnames
- Add backup and restore for Hub state and learner volumes
- Add immutable submission snapshots into Moodle only after the basic learning
  workflow has been validated

JupyterHub remains operationally separate from Moodle throughout these stages.
`moodle-rescue` owns the course content and integration scripts, while this
project owns code execution and live learner workspaces.
