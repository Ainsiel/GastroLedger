# Next.js Auth Session Guidance Skill

## Start By Detecting

- Confirm backend authentication and authorization contracts.
- Detect session library, cookie behavior, route protection and deployment topology.
- Never assume the frontend is the authorization authority.

## Procedure

1. Define secure session transport and server-side consumption.
2. Protect route groups and layouts while preserving backend authorization checks.
3. Define expiry, refresh, logout and unauthorized behavior.
4. Prevent tokens or sensitive session values from entering browser-accessible storage.
5. Define CSRF, duplicate submission and redirect safety where applicable.
6. Materialize only approved auth/session foundation boundaries.
7. Verify session behavior without exposing secrets.

## Rules

- Prefer HTTP-only, Secure and appropriate SameSite cookies when compatible.
- Backend authorization remains mandatory for every protected operation.
- Do not log tokens, cookies or secret values.

## Evidence

Record protected routes, session states, failure behavior and security findings.
