# Frontend Delivery Policy

## Trigger

This policy applies when an issue, work order or pull request:

- declares frontend scope;
- changes `apps/web/**`;
- adds or changes a user-visible route, component, state or interaction.

## Approved Sources

Frontend delivery must follow the repository's approved sources, in this order:

1. `docs/architecture/frontend/ui-design-spec.md`
2. `docs/architecture/frontend/frontend-architecture.md`
3. `docs/architecture/adrs/0007-shadcn-ui-system.md`
4. existing route, layout, design-token and shadcn/ui source conventions

Do not copy another product's brand, proprietary assets or interface. Do not add
external visual assets, APIs or services.

## Backlog Readiness Contract

A frontend-bearing issue is not `ready` until it identifies:

```text
observable user outcome
affected feature and route
approved UI sources
applicable visible states
responsive expectations
accessibility and keyboard expectations
frontend test evidence
visual QA evidence
```

The issue must require existing shadcn/ui-derived primitives and GastroLedger design
tokens. A new shared primitive is allowed only for a confirmed consumer and must not
contain domain behavior or transport calls.

## Work Order Contract

A frontend-bearing work order must include:

- affected frontend paths and route ownership;
- selected frontend skills: `nextjs-ui-design`, `nextjs-frontend-guidance` and
  `frontend-testing-strategy`, plus other confirmed skills when needed;
- Server/Client Component boundary and state ownership;
- API/error consumption contract;
- applicable loading, empty, validation/error, unauthorized, success,
  stale/conflict and destructive states;
- responsive verification at 390, 1024 and 1440 CSS pixels;
- keyboard, focus, accessible-name and status-announcement checks;
- component or feature tests plus integrated route evidence;
- visual QA evidence from the approved local environment.

Missing fields block implementation with `missing_frontend_delivery_contract`.

## Implementation Rules

- Use the approved `(app)` shell, route ownership and existing shared layouts.
- Use shadcn/ui-derived primitives and current design tokens before creating local
  alternatives.
- Keep route files focused on composition and client boundaries small.
- Preserve recoverable user input and make pending/result states visible.
- Do not ship unstyled browser-default forms or placeholder screens as completed UI.
- Do not enable actions for behavior that is not implemented.
- Follow behavior-first TDD through accessible public interactions.

## Verification Gate

The verifier must return `changes_requested` or `needs_more_evidence` when applicable
frontend evidence is missing or inconsistent with approved sources.

Passing frontend verification requires:

- route ownership and public boundaries remain correct;
- relevant component/feature tests and root checks pass;
- integrated route behavior is proven;
- keyboard and accessible-name behavior is covered;
- required visible states are demonstrated;
- visual QA at 390, 1024 and 1440 CSS pixels is recorded;
- no horizontal page scroll exists at 390 CSS pixels;
- no external visual dependency or unapproved component system was introduced.

Browser screenshots are preferred evidence. If the approved browser tool is
unavailable, record the limitation and provide equivalent integrated evidence; the
verifier decides whether that evidence is sufficient for the risk.
