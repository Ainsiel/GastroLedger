# Docker Compose Optimization Skill

## Purpose

Improve a confirmed Docker Compose workflow when startup time, build time, reliability or resource use causes measurable developer friction.

## Procedure

1. Define the common developer workflow and measured problem.
2. Capture baseline build/start/readiness behavior.
3. Identify whether the bottleneck is image build, dependency install, bind mounts, healthchecks, service coupling or resource pressure.
4. Propose the smallest Compose or Dockerfile change.
5. Validate config, startup, readiness, restart and clean teardown.
6. Measure the same workflow and record tradeoffs.

## Guidance

- Reuse Dockerfile cache through stable build contexts and ordered layers.
- Use profiles so optional tools do not burden the default workflow.
- Keep bind mounts narrow; avoid replacing container dependency directories accidentally.
- Use healthchecks with reasonable intervals, timeouts and retries.
- Avoid fixed sleeps for readiness.
- Keep services resilient to dependency restarts.
- Add resource limits only when supported and useful for the target environment.
- Keep logs bounded and useful.
- Make clean reset and persistent-data behavior explicit.

## Verification

Check:

```text
docker compose config
cold build and warm build
first startup and readiness
dependency restart
application restart
data persistence or reset
shutdown and orphan cleanup
```

## Forbidden

- Do not optimize without a baseline.
- Do not hide required services behind surprising profiles.
- Do not expose additional ports or secrets for convenience.
- Do not treat Compose as a production orchestrator unless explicitly decided.
