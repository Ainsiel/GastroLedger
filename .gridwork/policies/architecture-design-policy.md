# Architecture Design Policy

## Default

Choose the simplest architecture that satisfies confirmed drivers. Architecture skills are optional tools, not mandatory deliverables.

## Required Discipline

- Separate confirmed facts, assumptions, decisions and open questions.
- Trace every major decision to a requirement, quality attribute, constraint or risk.
- Prefer a modular monolith unless independent deployment, scaling, ownership or reliability needs justify distribution.
- Keep domain rules independent from frameworks and delivery mechanisms.
- Record consequential or hard-to-reverse choices as ADRs.
- Do not invent domain rules, scale targets or operational constraints.

## Human Gates

Ask before committing a decision when it materially changes system boundaries, data ownership, consistency, security, deployment or cost.

## Forbidden

- Pattern-driven design without a concrete problem.
- Microservices by default.
- One diagram or document per technique regardless of need.
- Treating framework packages as domain boundaries.
