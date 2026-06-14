# Frontend Testing Strategy Skill

## Procedure

1. Identify critical visible workflows and frontend failure modes.
2. Assign the narrowest useful test level to each behavior.
3. Cover component behavior, feature integration, API contracts and critical end-to-end paths.
4. Include keyboard, accessible-name and important state checks.
5. Test loading, empty, error, unauthorized, stale and destructive states.
6. Prefer public user interactions over implementation details.
7. Define evidence and confirmed commands.

## Coverage Model

```text
component behavior
feature integration
API contract consumption
critical end-to-end workflows
accessibility checks
```

## Verification

Reject brittle implementation-detail tests, excessive mocking, missing error states and
end-to-end coverage that duplicates cheaper tests without additional confidence.

## Output

Record behavior, selected test level, environment, real versus mocked boundaries,
accessibility expectation and evidence command.

## Gates

Stop before dependencies, shared environments, browser automation services or unknown
commands.

## Blocking Conditions

Block when the visible behavior, risk or test environment cannot be identified.
