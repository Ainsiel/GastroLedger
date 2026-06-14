# Gridwork Quickstart

1. Open `.gridwork/agents/orchestrator/PROMPT.md`.
2. Paste or reference that prompt in your coding agent chat.
3. Tell the orchestrator what request you want to work on.
4. Wait for the first routing response before asking it to act.
5. Approve any write, GitHub side effect or AFK delegation only when you are ready.

Gridwork installs governance, agents, workflows, skills, policies, stack guidance, schemas and templates. It does not create frontend, backend, database, Docker or application code.

After `architecture-ddd`, use `architecture-foundation` to create an approved minimal
executable structure before delegating functional TDD slices.

For a new monorepo, run `repository-bootstrap` before `architecture-foundation`, then
run `delivery-infrastructure` before feature PR delivery. Route failed required checks
through `ci-failure-repair`.

Feature work flows from `develop` through one work-order feature branch and CI-gated
PR. Production promotion uses a separately approved `develop -> main` release PR.

For workflow selection, examples and approval guidance, open
`.gridwork/docs/WORKFLOW_GUIDE.md`.
