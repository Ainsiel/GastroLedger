# Next.js App Router Architecture Skill

## Start By Detecting

- Confirm App Router, Next.js/React versions and deployment model.
- Inspect route groups, layouts, loading/error boundaries and client directives.
- Do not migrate from Pages Router without approval.

## Procedure

1. Map route groups and layouts to approved user workflows and access boundaries.
2. Default to Server Components; place client boundaries around the smallest interactive subtree.
3. Define loading, error, not-found, unauthorized and stale behavior per route.
4. Keep route files focused on composition rather than feature internals.
5. Define serialization boundaries and avoid unnecessary client bundle exposure.
6. Materialize only approved foundation routes and public feature surfaces.
7. Verify server/client boundaries and route ownership.

## Rules

- Do not add `"use client"` to broad layouts without evidence.
- Do not expose server-only values or secrets to client components.
- Do not use route groups as domain boundaries unless ownership aligns.

## Evidence

Record route ownership, layouts, server/client decisions, states and review findings.
