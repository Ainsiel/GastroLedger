# HTML Architecture Diagrams Skill

## Purpose

Render an approved architecture model as a self-contained, accessible and reviewable HTML diagram. This is the rendering foundation used by specialized C4, ERD and UML diagram skills.

## Procedure

1. Confirm the diagram goal, audience, type and source architecture artifacts.
2. Prepare `diagram-notes.md` with scope, assumptions and inventories.
3. Choose a layout that matches the information:
   - hierarchy or boundary map for ownership and C4;
   - graph or table-linked nodes for relationships;
   - horizontal lifelines for sequences;
   - lanes and decision nodes for flows;
   - state nodes and guarded arrows for lifecycles.
4. Start from `templates/architecture-diagram.html` when useful, then replace all placeholder content.
5. Write one HTML file with embedded CSS and optional embedded JavaScript.
6. Include a visible legend and a textual equivalent for important information.
7. Use stable dimensions and responsive overflow so labels remain readable.
8. Open locally without network, inspect desktop and narrow widths, and fix clipping or overlap.
9. Store drafts in `.factory/`; copy to `docs/architecture/diagrams/` only after approval.

## Visual Encoding

- Use color plus shape or border style; never rely on color alone.
- Use restrained semantic colors for approved, proposed, external, risk and deprecated.
- Use arrows with labels that explain the relationship.
- Group only when the boundary has architectural meaning.
- Keep the primary reading order obvious.

## Required HTML Content

```text
title and purpose
scope and status
diagram canvas
legend
element inventory
relationship inventory
assumptions and related decisions
```

## Rules

- Follow `diagram-html-policy.md`.
- No CDN, build step, package install or unapproved external assets.
- Do not invent architecture to make a diagram look complete.
- Do not create a diagram when a short table communicates the answer better.
