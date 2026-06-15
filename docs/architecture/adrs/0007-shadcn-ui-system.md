# ADR-0007: Use shadcn/ui As The Frontend Component Foundation

```text
status = accepted
```

## Decision

Use shadcn/ui-derived source components, Tailwind CSS and Lucide icons as the visual
component foundation for the GastroLedger Next.js application.

The components live inside `apps/web`, use GastroLedger-owned design tokens and remain
subject to existing route and feature ownership rules.

## Rationale

The current frontend has semantic behavior but no visual system. GastroLedger needs a
consistent, accessible and locally owned component foundation before additional
vertical slices add more user-facing workflows.

shadcn/ui provides auditable source components rather than a runtime black box and
allows the product to retain its own visual identity.

## Consequences

- Tailwind CSS, shadcn utility dependencies and Lucide become approved frontend
  dependencies.
- Only components with confirmed consumers are added.
- Shared UI primitives contain no domain behavior or transport calls.
- Updates to copied components are reviewed as repository source changes.
- The application does not copy another SaaS product's brand, assets or proprietary
  interface.

## Validation

- Frontend architecture tests continue to pass.
- Keyboard, responsive and visible-state checks cover the registration workflow.
- Production builds require no external UI asset service.

## Review Trigger

Revisit if the component source becomes difficult to maintain, accessibility evidence
regresses or a confirmed workflow cannot be represented without broad local forks.

