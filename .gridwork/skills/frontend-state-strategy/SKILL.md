# Frontend State Strategy Skill

## Procedure

1. Inventory state used by each user workflow.
2. Classify every state item as URL, server, local, global client or persistent browser state.
3. Assign one source of truth and ownership boundary.
4. Define synchronization, expiry, reset and failure behavior.
5. Require evidence before introducing global client state.
6. Keep sensitive and authorization state out of unsafe browser persistence.
7. Record the state ownership map and review triggers.

## Default Decisions

- Use URL state for shareable navigation and filters.
- Use server state for backend-owned data.
- Keep transient interaction state local.
- Use global client state only for confirmed cross-tree behavior.

## Verification

Reject duplicated sources of truth, unexplained global stores, stale server-state copies
and sensitive persistence.

## Output

Record state item, owner, source of truth, lifetime, synchronization, reset behavior and
failure recovery.

## Gates

Stop before adding a global store, browser persistence or duplicated server-state cache
without an explicit decision.

## Blocking Conditions

Block when ownership, sharing needs, privacy or freshness requirements are unknown.
