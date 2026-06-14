# SDD Requirements Skill

## Purpose

Consolidate completed ideation into an SDD-oriented requirements set that is precise enough for architecture design and acceptance testing.

## Readiness Gate

Before drafting, verify:

- the problem and target users are understood;
- scope and explicit exclusions exist;
- important terms are defined consistently;
- high-risk assumptions are visible;
- each major capability has at least one success scenario;
- unresolved questions are separated from accepted requirements.

If these conditions fail, return to ideation instead of filling gaps with invention.

## Procedure

1. Normalize ideation notes into facts, decisions, assumptions and questions.
2. Define problem, outcomes, actors, scope and exclusions.
3. Write uniquely identified functional requirements as observable behavior.
4. Write non-functional requirements as measurable quality scenarios.
5. Create use cases with trigger, preconditions, main flow, alternatives, failures and postconditions.
6. Derive acceptance and system test cases from each requirement and use case.
7. Build a traceability matrix from requirement to use case and test.
8. Record dependencies, constraints, risks and open questions.
9. Run a contradiction and ambiguity review.
10. Keep the draft in `.factory/` until the user approves it.

## Requirement Quality

Each requirement must be:

```text
necessary
unambiguous
observable
independently identifiable
traceable
feasible enough to architect
testable or explicitly non-testable
```

Avoid implementation decisions unless they are confirmed constraints. Use `must` only for approved requirements.

## Outputs

```text
requirements-overview.md
functional-requirements.md
quality-attributes.md
use-cases.md
test-cases.md
traceability-matrix.md
assumptions-and-open-questions.md
```

Approved files may be copied to `docs/sdd/`.

## Forbidden

- Do not invent requirements or resolve stakeholder conflicts silently.
- Do not use vague qualities such as "fast" or "secure" without scenarios or measures.
- Do not create issues or implement code.
