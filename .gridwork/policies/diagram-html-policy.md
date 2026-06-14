# HTML Diagram Policy

Architecture diagrams must be self-contained HTML documents that work from disk.

## Required

- No CDN, build step, package install or remote asset.
- Include title, purpose, scope, legend, generated date and source assumptions.
- Use semantic HTML and readable text at desktop and mobile widths.
- Provide a textual inventory or table equivalent for important relationships.
- Keep labels in the project's ubiquitous language.
- Mark uncertain or proposed elements explicitly.
- Link the diagram to related architecture documents or ADRs using relative paths when known.

## Validation

- Open locally without network access.
- Verify no clipped labels, overlapping elements or unreadable contrast.
- Verify every relationship has direction and meaning.
- Verify the visual matches the accompanying notes.

## Storage

Drafts live under `.factory/runs/<run-id>/artifacts/architecture/diagrams/`.
Only approved diagrams may be copied to `docs/architecture/diagrams/`.
