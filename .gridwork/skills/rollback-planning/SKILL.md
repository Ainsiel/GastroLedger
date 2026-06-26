# Rollback Planning

## Purpose

Define recovery criteria and procedures before production deployment.

## Procedure

1. Read deployment, artifact and migration strategies.
2. Define rollback and roll-forward trigger conditions.
3. Identify the previous trusted artifact and configuration.
4. Define database compatibility and data-loss constraints.
5. Define ownership, approvals and communication.
6. Define post-recovery health and smoke checks.
7. Record provider-specific steps only after provider approval.

## Evidence

- Produce a rollback plan and decision criteria.
- Record artifact and migration compatibility.
- Record verification and ownership.

## Guardrails

- Prefer backward-compatible migrations.
- Prefer roll-forward when rollback risks data loss.
- Never execute rollback or deploy without approval.
