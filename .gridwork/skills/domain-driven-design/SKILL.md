# Domain Driven Design Skill

## Purpose

Use DDD to discover business boundaries, ownership and consistency rules. Apply tactical patterns only where domain complexity justifies them.

## Procedure

Apply strategic design first. Use tactical design only inside contexts whose domain complexity justifies it.

### Strategic Design

1. Identify core, supporting and generic subdomains.
2. Find language changes, policy changes, ownership changes and consistency boundaries.
3. Propose bounded contexts around cohesive models, not around technical layers.
4. Give each context one clear purpose and owner.
5. Define upstream/downstream relationships and integration style.
6. Record a context map and the cost of each coupling.

### Tactical Design

For each complex context:

1. Identify use-case commands, queries and domain events.
2. Define aggregates around invariants requiring immediate consistency.
3. Keep aggregates small; reference other aggregates by identity.
4. Place domain behavior with the model that owns the rule.
5. Use repositories only for aggregate persistence abstractions.
6. Use domain services only for rules that genuinely span concepts.
7. Separate integration events from internal domain events when contracts differ.

## Required Questions

- Which business rule must never be violated?
- What must be consistent in one transaction?
- Who owns the data and language?
- Which changes should not force another context to change?
- What happens when an integration is delayed or unavailable?

## Outputs

Use `bounded-context-canvas.md` for each proposed context and produce:

```text
subdomain-map.md
context-map.md
bounded-contexts/<context>.md
aggregate-design.md
domain-events.md
```

## Avoid

- One bounded context per table, screen or microservice.
- Anemic entities containing only data.
- Large aggregates used as object graphs.
- Repositories for every table.
- DDD terminology where simple CRUD is sufficient.
