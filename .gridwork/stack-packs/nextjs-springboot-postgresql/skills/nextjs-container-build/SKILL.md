# Next.js Container Build

## Purpose

Define and verify a production-oriented Next.js runtime image.

## Procedure

1. Confirm frontend path and approved runtime mode.
2. Inspect lockfile, build scripts and ignore rules.
3. Prefer a multi-stage build.
4. Use standalone output when project-compatible.
5. Run the final image as a non-root user.
6. Start the image and execute its health contract.
7. Record image identity and verification evidence.

## Evidence

- Record build command, image identity and startup result.
- Record runtime user, port and health check.

## Guardrails

- Keep secret values out of build arguments and layers.
- Do not publish or deploy without approval.
- Do not generate during Gridwork installation.
