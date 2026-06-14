# Spring Boot Container Build

## Purpose

Define and verify a production-oriented Spring Boot runtime image.

## Procedure

1. Confirm backend path and approved Java runtime.
2. Build using the committed wrapper.
3. Copy only the runtime artifact into the final stage.
4. Run the final image as a non-root user.
5. Configure explicit entrypoint, port and health contract.
6. Start and smoke-test the image.
7. Record image identity and verification evidence.

## Evidence

- Record build command, image identity and startup result.
- Record runtime user and health check.

## Guardrails

- Do not leak internal actuator endpoints.
- Do not publish or deploy without approval.
- Do not generate during Gridwork installation.
