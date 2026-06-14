# Diagnose Bug Skill

## Purpose

Build a disciplined feedback loop, reproduce and explain a bug before planning or implementation.

## Procedure

1. Normalize expected behavior, observed behavior, environment and impact.
2. Build the fastest deterministic pass/fail feedback loop available.
3. Confirm the loop reproduces the user's actual symptom.
4. Minimize the input, state and steps while preserving the failure.
5. Generate three to five ranked falsifiable hypotheses.
6. Test one prediction at a time with the least invasive observation.
7. Identify the causal mechanism and affected scope.
8. Propose the regression test at the real behavioral boundary.
9. Record facts, eliminated hypotheses, remaining uncertainty and recommended next action.

## Feedback Loop Preference

Prefer, in order:

```text
existing failing test
narrow integration or API test
CLI or request replay
browser automation
captured trace replay
small throwaway harness
measured performance benchmark
structured HITL reproduction
```

Improve the loop before guessing: make it faster, sharper and more deterministic.

## Hypothesis Contract

Each hypothesis must state:

```text
suspected cause
evidence supporting it
prediction that would be true
probe that can falsify it
result
```

For performance bugs, establish a baseline and measure before recommending optimization.

## Workflow Boundaries

- In `intake-existing-code`, diagnose without modifying product code.
- In `tdd-implementation`, use the diagnosis to create the first RED regression test, then continue through `tdd`.
- In `verification-pr`, assess whether the regression test proves the reported failure.

## Outputs

```text
diagnosis-report.md
reproduction-steps.md
hypothesis-log.md
regression-test-recommendation.md
```

## Forbidden

- Do not modify code by itself.
- Do not present a plausible hypothesis as the root cause.
- Do not log secrets or copy uncontrolled production data.
- Do not optimize without a measurement.
