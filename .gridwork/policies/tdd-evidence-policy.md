# TDD Evidence Policy

## Required Evidence

```text
red_phase = required
green_phase = required
refactor_phase = required_when_refactor_performed
behavior_test_preferred = true
public_interface_preferred = true
tracer_bullet_for_vertical_slice = recommended
```

## Blocking Conditions

- No approved work order.
- No clear red phase.
- Unknown or non-allowlisted test command.
- Missing acceptance criteria.
- Scope change without approval.

## Verification Decision

If red or green evidence is missing, the verifier should use:

```text
decision = needs_more_evidence
```

## Frontend Evidence

For frontend-bearing work orders, evidence must also include accessible public
interaction tests, integrated route behavior and the visual QA required by
`frontend-delivery-policy.md`. Missing applicable frontend evidence produces
`needs_more_evidence`.
