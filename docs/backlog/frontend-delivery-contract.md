# Frontend Delivery Contract

```text
status = approved
applies_to = every backlog item with frontend scope
component_system = shadcn/ui-derived source components
```

This contract makes the approved GastroLedger UI direction executable for future
vertical slices. It supplements each issue's specific user outcome; it does not add
unrelated product behavior.

## Required Sources

- `docs/architecture/frontend/ui-design-spec.md`
- `docs/architecture/frontend/frontend-architecture.md`
- `docs/architecture/adrs/0007-shadcn-ui-system.md`
- existing `apps/web/components/ui`, layout components and design tokens

## Required Issue And Work Order Fields

Every frontend-bearing issue and work order must identify:

- affected feature and App Router route;
- primary user task and information hierarchy;
- Server/Client Component boundary and state ownership;
- API/error consumption contract;
- applicable loading, empty, validation/error, unauthorized, success,
  stale/conflict and destructive states;
- responsive behavior at 390, 1024 and 1440 CSS pixels;
- keyboard, focus, accessible-name and status-announcement expectations;
- component/feature tests, integrated route evidence and visual QA evidence.

## Implementation Rules

- Reuse the approved `(app)` workspace shell and existing feature ownership.
- Use shadcn/ui-derived primitives and GastroLedger tokens before adding components.
- Add shared primitives only for confirmed consumers.
- Keep visual components free of domain behavior and direct FastAPI calls.
- Do not ship unstyled browser-default forms, fake enabled actions or placeholder
  screens as completed UI.
- Preserve recoverable input and make pending and result states visible.
- Do not use external UI assets, APIs or services.

## Definition Of Done

- Relevant accessible behavior tests pass.
- The integrated route proves the observable user outcome.
- Required visible states are demonstrated.
- Keyboard-only operation and focus behavior are verified.
- Visual QA is recorded at 390, 1024 and 1440 CSS pixels.
- No horizontal page scrolling exists at 390 CSS pixels.
- `npm run lint`, `npm test`, `npm run build` and required PR checks pass.
