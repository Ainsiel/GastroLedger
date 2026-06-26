# Architecture Decision Records Skill

## Purpose

Record consequential decisions so future agents understand why the architecture has its current shape and when to revisit it.

## Create An ADR When

- a decision is expensive or risky to reverse;
- alternatives are plausible and future agents may re-litigate them;
- the decision changes ownership, consistency, deployment, security or public contracts;
- a deliberate constraint rejects an otherwise tempting approach.

## Procedure

1. State the decision question neutrally.
2. Describe context and drivers without rewriting the whole SDD.
3. Compare real considered options, including the simplest baseline.
4. Record the selected decision in one direct statement.
5. List positive, negative and operational consequences.
6. Define validation evidence and a review trigger.
7. Link related requirements, diagrams and ADRs.
8. Keep status `proposed` until approved.

## Rules

- One primary decision per ADR.
- Do not hide disadvantages.
- Do not use ADRs for temporary task notes.
- Supersede old ADRs; do not rewrite accepted history silently.
- Use `adr.md` and a stable numeric filename.
