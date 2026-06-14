# Architecture Conformance Verification Skill

## Procedure

1. Read approved architecture, ADRs, foundation plan and relevant changed files.
2. Verify dependency direction, module ownership and public boundaries.
3. Confirm every foundation abstraction has an approved source and known consumer.
4. Detect business behavior, speculative abstractions and unapproved architecture changes.
5. Review architecture-test evidence and run approved checks when allowed.
6. Produce `pass`, `changes_requested` or `needs_more_evidence`.

Do not resolve architecture contradictions during verification; report them for an
explicit decision.

## Findings Order

Report findings in this order:

1. Unapproved architecture decisions or boundary violations.
2. Business behavior introduced during foundation.
3. Speculative abstractions without consumers.
4. Missing or weak architecture-test evidence.
5. Documentation and traceability gaps.

## Decision Rule

Use `changes_requested` for confirmed violations and `needs_more_evidence` when
conformance cannot be established.

## Output

Use `architecture-conformance-report.md` and include exact evidence paths.
