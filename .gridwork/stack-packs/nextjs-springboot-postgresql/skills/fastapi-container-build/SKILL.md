# FastAPI Container Build

## Purpose

Define and verify a production-oriented FastAPI runtime image.

## Procedure

1. Confirm backend path and approved Python runtime.
2. Install from locked dependencies.
3. Copy only required runtime files.
4. Run the final image as a non-root user.
5. Define explicit ASGI startup and health contract.
6. Start and smoke-test the image.
7. Record image identity and verification evidence.

## Evidence

- Record build command, image identity and startup result.
- Record runtime user, workers and health check.

## Guardrails

- Keep worker and proxy behavior environment-configurable.
- Do not publish or deploy without approval.
- Do not generate during Gridwork installation.
