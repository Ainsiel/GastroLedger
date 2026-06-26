# Stack Skill Policy

## Installation Rule

Gridwork `init` installs stack skill definitions only. It never creates frontend, backend, database or Docker product files.

## Use Rule

Stack skills may guide architecture, implementation or verification only after the project technology and real paths are confirmed.

- Architecture use produces recommendations and decisions.
- Implementation use may modify scoped product files only through an approved work order.
- Verification use is read-only and reports findings.

Stack skills never expand agent permissions, path scopes or command allowlists.

## Version Awareness

Detect project versions and existing conventions before recommending framework-specific APIs. Do not silently upgrade dependencies.

## Forbidden

- Generating a new project during `init`.
- Assuming stack paths from hints.
- Installing dependencies without approval.
- Replacing working project conventions without a documented reason.
