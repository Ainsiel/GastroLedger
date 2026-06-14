# Frontend API Contract Consumption Skill

## Procedure

1. Identify frontend consumers for each approved backend contract.
2. Define typed transport boundaries and explicit DTO-to-view mapping.
3. Normalize validation, authorization, conflict and unexpected errors.
4. Define loading, retry, cancellation and duplicate-submission behavior.
5. Keep transport details outside visual components.
6. Define compatibility and contract-test expectations.
7. Record consumer ownership and error behavior.

## Rules

- Do not expose backend transport DTOs as unrestricted frontend domain models.
- Do not retry non-idempotent mutations blindly.
- Do not treat frontend checks as authorization.
- Keep mocks limited to test boundaries and never present them as production behavior.

## Verification

Review typed boundaries, error handling, compatibility, retries and consumer ownership.

## Output

Record consumers, transport types, view mappings, normalized errors, retry rules,
cancellation behavior and compatibility tests.

## Gates

Stop before changing a public backend contract, adding blind retries or exposing
sensitive transport fields.

## Blocking Conditions

Block when the backend contract, error semantics or owning frontend feature is unclear.
