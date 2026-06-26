# Agent Catalog

| Agent | Mode | Purpose |
|---|---|---|
| orchestrator | interactive | Route requests, enforce gates and delegate. |
| intake-agent | interactive | Clarify ideas, bugs, features and improvements. |
| software-architect | interactive | Design DDD architecture and ADRs. |
| architecture-foundation-agent | hybrid | Materialize approved architecture without business behavior. |
| planner-agent | hybrid | Create backlog drafts and publish plans. |
| backlog-manager-agent | interactive | Inspect, manage and select work from local and GitHub backlog. |
| implementer-agent | afk | Implement approved work orders with TDD. |
| verifier-agent | hybrid | Review evidence and PRs without modifying code. |
| release-manager-agent | hybrid | Promote verified develop state to main and observe production deployment. |
| platform-engineer-agent | hybrid | Bootstrap the monorepo and operate approved delivery infrastructure. |

Skills never raise agent permissions.

Key capability assignments:

- `implementer-agent` uses `tdd` for implementation and may use `git-branch-management` only under gates.
- `verifier-agent` uses `tdd` only to assess evidence and never fixes code.
- `planner-agent` uses `github-label-manager` to audit predefined labels before issue publication.
- `backlog-manager-agent` maintains a unified local/GitHub backlog view and prepares approved implementation handoffs.
- `orchestrator` may prepare Git action plans after verification, but never merges.
- `orchestrator` coordinates approved feature PR merges to `develop`; `release-manager-agent` coordinates approved release merges to `main`.
- `software-architect` starts with `architecture-grill-me`, then selects only architecture and diagram skills justified by confirmed drivers.
- When a frontend exists, `software-architect` explicitly designs feature/route ownership, state, API consumption, auth boundaries and tests.
- `architecture-foundation-agent` creates only the approved minimal executable structure, required contracts, composition root and architecture tests.
- `software-architect`, `architecture-foundation-agent`, `implementer-agent` and `verifier-agent` may use integration testing and stack-pack skills after technology and paths are confirmed.
- `architecture-foundation-agent` materializes approved frontend boundaries without functional screens; implementer and verifier apply the frontend strategy per slice.
- `planner-agent` and `backlog-manager-agent` cannot mark frontend-bearing work ready
  until the frontend delivery contract is complete.
- `implementer-agent` and `verifier-agent` must enforce approved UI sources,
  shadcn/ui usage, responsive/accessibility behavior and visual QA evidence.
- `platform-engineer-agent` creates approved framework scaffolds, root quality commands, Compose environments and GitHub Actions without implementing business behavior.

Ask `backlog-manager-agent` for the current backlog, remaining or blocked tasks,
missing work, or a recommended next task. A request to take a task prepares a work
order candidate; approval and delegation to `implementer-agent` remain separate gates.
