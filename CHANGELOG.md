# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- Make the Moodle assignment submission bridge explicitly optional and include
  its service implementation in clean production Hub images.
- Validate HTTPS submission settings before production startup.

### Security

- Document that guest-readable Moodle courses do not provide anonymous Python
  Lab execution; every Lab workspace requires an authenticated Moodle LTI
  identity.

## [0.1.0-alpha.1] - 2026-08-27

### Added

- Reproducible JupyterHub and DockerSpawner environment for WSL-hosted Docker.
- Persistent per-learner workspaces and versioned course-material updates.
- Moodle LTI 1.3 integration for local development.
- Bilingual lesson notebooks, project starters, sample data, and self-checks.
- Invite-only pilot configuration for the independent Traefik Rescue gateway.
- Production Compose and startup invariants that require HTTPS LTI endpoints.

### Known limitations

- Alpha quality; interfaces and course files may still change.
- Same-host production is intended only for a small, invite-only pilot.
- Backup scheduling, high availability, and broad public hardening are not bundled.
- Python Lab requires network access and does not provide an offline mode.
