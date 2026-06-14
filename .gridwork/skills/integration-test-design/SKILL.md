# Integration Test Design Skill

## Purpose

Design technology-agnostic integration test boundaries, scenarios, environments and
evidence before implementation begins.

## Procedure

1. Start from an observable behavior, contract, risk or acceptance criterion.
2. Identify the components and real boundary whose collaboration must be proven.
3. Choose the narrowest scope that exposes the target integration risk.
4. Define collaborators that must be real and external systems that need controlled substitutes.
5. Define success, validation, failure, timeout, retry and concurrency scenarios as relevant.
6. Design deterministic setup, representative data, isolation and cleanup.
7. Define environment lifecycle, schema/migration needs and resource ownership.
8. Select evidence and diagnostics that will make failures actionable.
9. Identify broader end-to-end or contract tests that remain outside scope.
10. Review cost, speed, reliability and maintenance tradeoffs.

## Strategy Contract

```text
behavior_or_contract
boundary_under_test
real_collaborators
controlled_substitutes
environment_and_lifecycle
data_and_isolation
scenarios
commands_to_confirm
evidence
out_of_scope
```

## Design Rules

- Design around a meaningful collaboration, not around framework startup.
- Prefer one owned, deterministic environment over a shared mutable environment.
- Keep fixtures minimal and representative.
- Plan failure diagnostics before creating a large suite.
- Separate integration, contract and end-to-end responsibilities explicitly.
- Treat dependency additions and shared environment use as human gates.

## Outputs

```text
integration-test-strategy.md
integration-test-cases.md
integration-environment-plan.md
```

## Forbidden

- Do not assume a testing framework or container tool.
- Do not require real third-party systems without approval.
- Do not include secrets or uncontrolled production data.
- Do not design tests that assert only internal implementation details.

