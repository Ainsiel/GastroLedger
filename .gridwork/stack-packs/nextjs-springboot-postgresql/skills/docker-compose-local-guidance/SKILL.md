# Docker Compose Local Guidance

## Purpose

Guide creation, review and verification of Docker Compose environments for reproducible local development and integration testing.

## Start By Detecting

- existing Compose files and Compose specification usage;
- Dockerfiles, build contexts and target stages;
- required services, ports, data and startup dependencies;
- environment examples and secret policy;
- confirmed infra paths and commands.

## Compose Design

- Keep the default profile sufficient for the common local workflow.
- Use services with one clear responsibility.
- Use healthchecks that verify readiness, not only process existence.
- Use dependency conditions only when supported and still make applications resilient to delayed dependencies.
- Use named volumes for persistent developer data and bind mounts only where live editing is intended.
- Expose only ports developers need.
- Use internal networks and service names for container-to-container traffic.
- Use profiles for optional tooling.
- Keep environment-specific overrides explicit.

## Database And Migrations

- Use a pinned PostgreSQL version.
- Make data reset and migration workflows deliberate.
- Do not embed real credentials; use local examples or generated development-only values.
- Avoid relying on `latest`.

## Verification

- Validate with project-approved `docker compose config`.
- Check startup, readiness, restart, clean shutdown and data persistence behavior.
- Verify service logs are useful and do not expose secrets.

## Rules

- Gridwork `init` does not create Compose files.
- An approved `repository-bootstrap` plan or implementation work order may create or modify confirmed Compose paths.
- Do not deploy, read secrets or elevate permissions.
