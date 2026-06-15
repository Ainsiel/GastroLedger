# GastroLedger UI Design Spec

```text
status = approved for implementation
frontend = Next.js App Router
component_system = shadcn/ui
visual_direction = calm operational SaaS for restaurant groups
```

## Users And Primary Workflows

The first visible workflow serves a prospective tenant administrator registering a
restaurant group. Future authenticated screens serve managers and operators who need
high information density, obvious status and low decision friction.

The interface must feel trustworthy and operational without presenting accounting,
payroll, payment, external integration or other capabilities outside the approved
GastroLedger scope.

## Visual Direction

- Original GastroLedger identity informed by common operational SaaS patterns, not a
  copy of another product's brand, assets or layout.
- Warm neutral surfaces with a deep charcoal navigation color and copper/amber primary
  actions.
- Compact, calm typography and spacing suitable for daily operational work.
- Color is used for status and action priority, never as the only source of meaning.
- Cards frame meaningful groups only; nested decorative cards are avoided.
- Empty states describe unavailable or not-yet-configured capabilities honestly.

## Information Hierarchy

### Public Experience

1. GastroLedger identity and concise value proposition.
2. Primary registration action.
3. Trust statements: local operation, tenant isolation and traceable activity.
4. Registration form grouped into company, administrator and optional first branch.
5. Visible submission and result status.

### Authenticated Shell

1. Current tenant and branch context.
2. Primary bounded-context navigation.
3. Page title, short purpose and contextual actions.
4. Operational content and explicit states.

The authenticated shell may expose navigation labels for approved bounded contexts,
but it must not imply that unimplemented workflows are functional.

## Route And Component Ownership

| Area | Owner | Main components |
|---|---|---|
| `/` | route composition | public header, value proposition, approved capability summary |
| `(public)/register` | onboarding | registration form, field groups, result alert |
| `(app)` layouts | route composition | workspace shell, bounded-context navigation |
| `components/ui` | shared visual primitives | shadcn-derived primitives only |
| `components/layout` | shared confirmed layout | public header, workspace shell, empty workspace |

Visual components do not call FastAPI. Transport behavior remains inside the owning
feature boundary.

## Responsive Layout

| Width | Behavior |
|---|---|
| `< 640px` | Single-column content, compact header, full-width primary actions |
| `640px-1023px` | Two-column public hero where useful; forms remain readable |
| `>= 1024px` | Public split layout and persistent authenticated sidebar |

No route may introduce horizontal page scrolling at 390 CSS pixels.

## Components And Interactions

- shadcn/ui-derived `Button`, `Input`, `Label`, `Card`, `Alert`, `Badge` and
  `Separator` provide the initial primitive set.
- Lucide icons support familiar navigation and status concepts and always retain an
  accessible label where the icon is the only visible control.
- Registration uses native form semantics, visible labels and browser autocomplete.
- Submission disables the primary action and preserves recoverable input.
- Destructive styling is reserved for destructive actions and errors.

## States

| Area | Loading | Empty | Error | Unauthorized | Success |
|---|---|---|---|---|---|
| Registration | Disabled submit with progress label | N/A | Field guidance plus visible summary | N/A | Tenant-ready confirmation |
| Public home | N/A | Honest capability overview | N/A | N/A | Registration CTA |
| Workspace shell | Skeleton-ready structure | Explicit not-yet-implemented state | Correlation-aware alert | Authentication-required state | Scoped tenant context |

Unexpected errors expose a correlation ID when available. Validation states never
erase the submitted form.

## Accessibility And Keyboard

- Every input has a visible label and useful autocomplete metadata.
- Focus styles remain visible on all interactive elements.
- Keyboard order follows visual order.
- Status changes use `role="status"` or `role="alert"` as appropriate.
- Touch targets are at least 40 CSS pixels high.
- Text and controls meet WCAG AA contrast expectations.
- Reduced-motion preferences disable non-essential transitions.

## Visual QA Checklist

- Review `/` and `/register` at 390, 1024 and 1440 CSS pixels.
- Complete registration using keyboard only.
- Inspect idle, submitting, success, duplicate, validation and unexpected states.
- Confirm long tenant names and error messages wrap without clipping.
- Confirm no unimplemented action appears enabled.
- Confirm production build output contains no external visual asset dependency.

## Delivery Gate For Future Slices

Every backlog issue and work order with frontend scope must satisfy
`docs/backlog/frontend-delivery-contract.md`.

An issue is not ready, and a verifier must not pass it, unless the affected route,
applicable visible states, shadcn/ui usage, responsive/accessibility expectations,
frontend tests and visual QA evidence are explicit.
