# Next.js Data Fetching And Cache Skill

## Start By Detecting

- Confirm Next.js version, router, existing data libraries and deployment behavior.
- Identify freshness, privacy and mutation requirements for each workflow.

## Procedure

1. Decide server versus client fetching from security, interactivity and freshness needs.
2. Define cache, revalidation and invalidation from product semantics.
3. Define mutation pending, success, failure, retry and duplicate-submission behavior.
4. Use optimistic updates only with explicit rollback and consistency behavior.
5. Avoid sequential waterfalls when independent fetches can run concurrently.
6. Prevent user-specific or sensitive responses from unsafe caching.
7. Verify the current implementation against the strategy.

## Selection Rules

- Prefer server fetching for secure initial data when appropriate.
- Use client fetching for ongoing interactive synchronization when justified.
- Do not introduce a data library without a confirmed need and approval.
- Do not rely on accidental framework cache defaults.

## Evidence

Record ownership, freshness, invalidation, mutation and stale-state behavior.
