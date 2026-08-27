# Security boundary

The local Compose environment is a development proof of concept. It binds the
Hub only to `127.0.0.1` and refuses local authentication unless
`LAB_LOCAL_DEVELOPMENT=true` and a non-placeholder password of at least 16
characters are supplied.

In local LTI mode, a fixed-purpose `moodle-jwks-proxy` fetches only the Moodle
public signing-key document from the loopback-published Moodle container. It
is not a general HTTP proxy, is not published to the host, and shares a private
service network only with the Hub. This workaround is local-development
infrastructure; the final deployment must use direct HTTPS endpoints instead.

DockerSpawner requires control of the Docker daemon. The Hub service
mounts `/var/run/docker.sock` into the Hub and must not be exposed to untrusted
networks. Compromise of the Hub must be treated as potential compromise of the
Docker host.

Learner containers use an internal Docker network, drop Linux capabilities,
enable `no-new-privileges`, and receive CPU, memory, and process limits. They do
not receive the Docker socket, Moodle volumes, Moodle credentials, or host bind
mounts. Only their named notebook volume persists.

For an internet-facing pilot, use Moodle LTI 1.3 through HTTPS, remove the
local JWKS workaround, define backup and restore procedures, and complete a
threat review. Before serving a wider or less trusted audience, isolate Docker
control on a dedicated host or stronger daemon boundary and test incident
recovery.
Do not reuse the local password in any deployed environment.
