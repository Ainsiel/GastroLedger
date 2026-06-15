# Next.js E2E Testing

## Purpose

Define browser-level evidence for critical Next.js user flows.

## Procedure

1. Select flows from approved acceptance criteria.
2. Define isolated fixtures and authentication setup.
3. Exercise behavior through public browser interactions.
4. Keep selectors stable and user-oriented.
5. Capture traces, screenshots or logs on failure.
6. Exercise approved responsive viewports and keyboard-only interaction when the
   frontend delivery contract requires them.
7. Run against the approved integrated environment.
8. Record results and remaining coverage gaps.

## Evidence

- Record tested flows, environment and artifacts.
- Record tested viewports, visible states and visual evidence.
- Record failures with reproducible steps.

## Guardrails

- Do not replace focused lower-level tests with broad E2E tests.
- Do not use shared production data.
- Do not generate during Gridwork installation.
