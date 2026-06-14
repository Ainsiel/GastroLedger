# Integration Testing Skill

## Purpose

Design, implement or assess integration tests that prove observable behavior across
real boundaries while remaining independent of a particular framework or language.

## Procedure

1. State the behavior or contract and the boundaries that must integrate.
2. Choose the narrowest test scope that still crosses the real risk-bearing boundary.
3. Identify required infrastructure, lifecycle, data, isolation and cleanup.
4. Prefer real collaborators inside the selected boundary; replace only external,
   unsafe, unavailable or nondeterministic systems with controlled substitutes.
5. Define success, validation, failure, retry and concurrency cases as applicable.
6. Make setup deterministic and keep fixtures minimal, explicit and reusable.
7. Use the public interface and assert externally meaningful results and side effects.
8. Run only confirmed allowlisted commands and record concise evidence.
9. Verify repeatability, isolation and failure diagnostics.
10. Document gaps that require broader end-to-end or contract testing.

## Boundary Selection

Possible integration boundaries include:

```text
HTTP or message adapter -> application behavior
application behavior -> persistence
service -> real database
producer -> consumer contract
multiple modules inside one deployable unit
containerized local dependencies
```

Do not call a test integration-level merely because it starts a framework. The test
must cross a meaningful boundary and prove a real collaboration.

## Test Design Rules

- Keep each test focused on one observable behavior.
- Isolate state between tests and make cleanup reliable.
- Use representative schemas and migrations.
- Avoid real third-party or shared production-like systems without approval.
- Control time, randomness and asynchronous completion explicitly.
- Prefer diagnostic assertions over broad snapshots.
- Keep tests deterministic before optimizing their speed.

## Implementation And Verification

Inside `tdd-implementation`, use this skill with `tdd` to create the RED/GREEN cycle.
Inside `verification-pr`, assess boundary realism, isolation, repeatability and
coverage without modifying code.

## Outputs

```text
integration-test-strategy.md
integration-test-cases.md
integration-test-evidence.md
```

## Forbidden

- Do not install test dependencies without approval.
- Do not use secrets or uncontrolled production data.
- Do not run against shared environments without an explicit gate.
- Do not replace every collaborator with mocks and claim integration coverage.

