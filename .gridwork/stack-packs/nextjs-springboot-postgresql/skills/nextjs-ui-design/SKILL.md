# Next.js UI Design Skill

## Purpose

Design or review a polished Next.js interface that fits the product domain, existing design system and real user workflow.

## Procedure

1. Identify audience, primary task, frequency of use and decision pressure.
2. Inspect existing visual language, components, icons and tokens.
3. Read and follow the approved UI design spec, frontend architecture and component
   system decision when they exist.
4. Map the workflow, information hierarchy and required states before styling.
5. Choose layout density and interaction patterns appropriate to the domain.
6. Define responsive behavior from narrow mobile through wide desktop.
7. Specify loading, empty, error, offline, unauthorized, success and destructive states.
8. Implement or review with semantic HTML, accessible names and keyboard behavior.
9. Verify text fit, focus order, contrast, reduced motion and touch targets.
10. Validate through screenshots and behavior tests when available.

## Design Rules

- Make the primary task immediately discoverable.
- Prefer established controls: icons for familiar tools, tabs for views, toggles for binary settings and menus for option sets.
- Use cards only for genuinely repeated or framed items; avoid card nesting.
- Keep operational tools dense, calm and scannable.
- Reserve hero-scale typography for real hero experiences.
- Use visual assets only when they help inspect the actual product, object or state.
- Keep destructive actions distinct and confirm consequential actions.
- Do not describe the interface's own styling or controls in visible helper text.
- Reuse the approved component system and tokens before creating alternatives.
- Do not accept unstyled browser-default controls or placeholder pages as completed
  product UI unless the approved design spec explicitly requires them.

## Next.js Rules

- Keep interactive client boundaries small.
- Ensure server-rendered and hydrated output remain consistent.
- Use framework image, font and metadata capabilities when already configured.
- Do not add a UI library or icon package without approval.

## Verification

Review at minimum:

```text
primary workflow
keyboard-only workflow
mobile and desktop
long content and localization risk
loading, empty and error states
validation and destructive actions
approved component-system consistency
visual QA evidence at required viewports
```
