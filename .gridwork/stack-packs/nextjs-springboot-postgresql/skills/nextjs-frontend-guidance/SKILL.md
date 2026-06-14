# Next.js Frontend Guidance

## Purpose

Guide architecture, implementation and verification for an existing or manually created Next.js project.

## Start By Detecting

- Next.js and React versions;
- App Router or Pages Router;
- rendering and deployment model;
- existing design system, data client, auth and test tools;
- confirmed frontend paths and project commands.

Do not silently migrate routers, libraries or conventions.

## Structure

- Organize user-facing features around domain capabilities.
- Keep route files focused on composition and routing.
- Default to Server Components in App Router; add `"use client"` only at the smallest interactive boundary.
- Keep domain-independent UI primitives separate from feature components.
- Keep transport DTOs and API clients out of visual components.
- Validate environment variable exposure; only explicitly public values reach the browser.

## Data And State

- Fetch on the server when it improves security, latency or bundle size.
- Define caching and revalidation intentionally; do not rely on accidental defaults.
- Keep URL state for shareable navigation/filter state.
- Keep local transient UI state local.
- Avoid global client state for server-owned data unless a confirmed need exists.
- Handle loading, empty, error, unauthorized and stale states.

## Forms And Mutations

- Validate at the client for usability and at the server for trust.
- Make pending, success, validation and failure behavior explicit.
- Prevent duplicate submissions for non-idempotent actions.
- Preserve user input after recoverable errors.

## Verification

- Test observable behavior through routes and accessible interactions.
- Verify server/client boundary, error states, responsive layout and keyboard access.
- Run only project-confirmed commands.

## Rules

- Gridwork `init` does not generate a Next.js project.
- Implementation may edit confirmed scoped files only under an approved work order.
- Do not assume paths, install packages or elevate permissions.
