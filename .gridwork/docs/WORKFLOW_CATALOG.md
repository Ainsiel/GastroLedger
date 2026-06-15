# Workflow Catalog

For practical prompts, examples, workflow transitions and approval guidance, see
`WORKFLOW_GUIDE.md`.

| Workflow | Mode | Primary Agent |
|---|---|---|
| intake-existing-code | interactive | intake-agent |
| ideation-from-zero | interactive | intake-agent |
| architecture-ddd | interactive | software-architect |
| architecture-foundation | hybrid | architecture-foundation-agent |
| backlog-management | interactive | backlog-manager-agent |
| backlog-task-delivery | hybrid | orchestrator |
| tdd-implementation | afk | implementer-agent |
| verification-pr | hybrid | verifier-agent |
| feature-pr-delivery | hybrid | orchestrator |
| release-promotion | hybrid | release-manager-agent |
| repository-bootstrap | hybrid | platform-engineer-agent |
| delivery-infrastructure | hybrid | platform-engineer-agent |
| ci-failure-repair | hybrid | platform-engineer-agent |

There is no agent workflow named `cicd-release` in v1. CI/CD is handled as GitHub Actions YAML with the `github-actions-cicd` skill.

`tdd-implementation` uses the reusable `tdd` skill. Git actions after implementation or verification use `git-branch-management` and remain behind separate approval gates.

`backlog-management` consolidates local drafts and governed GitHub issue reads, answers backlog questions and prepares an approved task handoff to `tdd-implementation`.

Frontend-bearing backlog work is ready only after it satisfies
`frontend-delivery-policy.md`. Implementation and verification must preserve that
contract through visual QA evidence.

`backlog-task-delivery` composes `backlog-management`, `tdd-implementation`, `feature-pr-delivery` and `verification-pr` for a single request to select, implement, verify and merge a ready task into `develop`. Work-order approval and AFK delegation remain explicit gates.

`feature-pr-delivery` keeps a feature PR open through CI and verifier correction cycles, then performs an approved squash merge to `develop`.

`release-promotion` governs `develop -> main`, full release CI, production approval and deployment verification.

`architecture-ddd` starts with an adaptive grill-me. DDD strategic design is central; Clean Architecture, patterns, APIs, data models, stack guidance and C4/ERD/UML HTML diagrams are optional capabilities selected only when needed.

When a frontend is present, `architecture-ddd` must also produce explicit frontend
feature boundaries, route ownership, execution boundaries, state strategy, API
consumption, security boundary and test strategy.

`architecture-foundation` materializes approved boundaries as a minimal executable structure, required contracts, composition root and architecture tests. It explicitly forbids business behavior and speculative abstractions.

`repository-bootstrap` prepares approved framework roots, root quality commands, containers and Compose environments before architecture foundation or feature work.

`delivery-infrastructure` materializes reusable GitHub Actions, required-check plans, ruleset plans and environment protections.

`ci-failure-repair` diagnoses failed checks for the current PR SHA and routes the smallest repair back to the owning implementer.
