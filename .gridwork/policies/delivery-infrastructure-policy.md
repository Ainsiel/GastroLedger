# Delivery Infrastructure Policy

## Branch Contract

```text
feature/<work-order-id>-<slug> -> develop -> main
```

- Feature PRs require the current head SHA to pass `feature / regression-gate` before verifier review.
- Every corrective push invalidates previous CI and verifier evidence.
- Release PRs from `develop` to `main` run the full regression suite without changed-path shortcuts.
- Production deployment starts only from an approved commit on `main`.

## Monorepo Contract

- Keep independently testable components in explicit top-level boundaries such as `frontend/`, `backend/`, `tests/` and `infra/`.
- Expose stable root quality commands; CI calls those commands instead of duplicating stack internals.
- Use reusable workflows for component checks.
- Use changed-scope detection only for feature PR optimization.

## Compose Contract

- Use a base Compose file plus environment overlays.
- Use profiles for optional services, not as the only environment separation mechanism.
- Never store production secrets in Compose files.

## Remote Contract

GitHub workflow writes, rulesets, environments, pushes, PRs, merges, releases and deploys require explicit approval.
