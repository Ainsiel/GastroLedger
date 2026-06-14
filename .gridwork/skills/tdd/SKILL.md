# TDD Skill

## Purpose

Execute or assess test-driven development as small vertical cycles that prove observable behavior through public interfaces.

## Core Rules

- Start only from an approved work order with acceptance criteria, path scopes and allowlisted commands.
- Convert acceptance criteria into prioritized observable behaviors.
- Run one tracer-bullet cycle at a time: one behavior, one failing test, minimal implementation, green result.
- Prefer integration-style behavior tests through public interfaces.
- Do not test private methods, internal call order or accidental structure.
- Mock only real external boundaries when using the real boundary is unsafe, unavailable or nondeterministic.
- Refactor only while green and rerun the relevant tests after each refactor step.
- Record commands and concise evidence; never copy secrets or uncontrolled logs.

## Procedure

1. Validate the work order and stop if a required contract field is missing.
2. Write `.factory/runs/<run-id>/artifacts/tdd/tdd-plan.md`.
3. Select the smallest behavior that proves an end-to-end path.
4. Add or activate one test and run the narrowest allowlisted command.
5. Confirm RED failed for the expected behavioral reason.
6. Implement the minimum change needed for GREEN.
7. Run the same test and record GREEN.
8. Repeat one behavior at a time.
9. Refactor only after green, without expanding scope.
10. Run final allowlisted checks and complete `tdd-evidence.md`.

## RED Gate

Block when the test:

- passes before implementation;
- fails because of setup, syntax, environment or unrelated behavior;
- asserts implementation details instead of the requested behavior;
- requires a command outside the allowlist.

An exception is allowed only for an explicitly non-testable or documentation-only work order. Record justification and mark `needs_more_evidence`.

## Verification Use

The verifier may use this skill to assess evidence, but must not modify code. Verify:

- RED and GREEN use the same relevant behavior;
- the failing reason is expected;
- each cycle is vertical rather than a batch of tests followed by a batch of implementation;
- refactor happened only after green;
- final checks cover the acceptance criteria.

## Outputs

```text
.factory/runs/<run-id>/artifacts/tdd/tdd-plan.md
.factory/runs/<run-id>/artifacts/tdd/tdd-evidence.md
.factory/runs/<run-id>/artifacts/implementation-summary.md
```

## Forbidden

- Do not write all tests first and all implementation afterward.
- Do not silently skip RED or GREEN.
- Do not add speculative behavior.
- Do not install dependencies or expand scope without approval.
- Do not use this skill to raise agent permissions.
