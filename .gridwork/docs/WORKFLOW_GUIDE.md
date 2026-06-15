# Workflow Usage Guide

This guide explains how to use Gridwork workflows through a coding-agent chat.
Gridwork has no `gridwork run` command. The orchestrator reads the installed factory,
routes the request and proposes the correct workflow before acting.

## Start Gridwork

Open `.gridwork/agents/orchestrator/PROMPT.md`, paste or reference it in the coding
agent chat, then describe the work.

Example:

```text
Read .gridwork/agents/orchestrator/PROMPT.md and act as the Gridwork orchestrator.
I want to understand why checkout requests sometimes create duplicate orders.
```

The first response should identify:

```text
detected request type
proposed workflow and agent
routing confidence
missing context
approval gates
next step
```

The orchestrator must wait before code changes, GitHub writes or AFK delegation.

## Choose A Workflow

| Your situation | Workflow | Primary agent | Mode |
|---|---|---|---|
| A bug, feature or improvement in existing code needs clarification | `intake-existing-code` | `intake-agent` | interactive |
| A new product idea needs requirements and an SDD | `ideation-from-zero` | `intake-agent` | interactive |
| An approved SDD needs architecture and technical decisions | `architecture-ddd` | `software-architect` | interactive |
| Approved architecture must become an executable foundation | `architecture-foundation` | `architecture-foundation-agent` | hybrid |
| You want backlog status, gaps or a task selected | `backlog-management` | `backlog-manager-agent` | interactive |
| You want a pending task selected, implemented and verified | `backlog-task-delivery` | `orchestrator` | hybrid |
| An approved work order is ready to implement | `tdd-implementation` | `implementer-agent` | AFK |
| A completed work order must pass PR CI and merge to develop | `feature-pr-delivery` | `orchestrator` | hybrid |
| An implementation or PR needs review | `verification-pr` | `verifier-agent` | hybrid |
| Verified develop state must be promoted to production | `release-promotion` | `release-manager-agent` | hybrid |

When uncertain, describe the outcome instead of naming a workflow. The orchestrator
should route the request and explain its choice.

## Shared Operating Model

Every workflow follows the same broad pattern:

1. The orchestrator understands and routes the request.
2. The responsible agent confirms inputs and missing context.
3. Drafts and runtime evidence stay under `.factory/runs/<run-id>/`.
4. The workflow stops at relevant human gates.
5. Approved documents may be promoted to versioned `docs/` paths.
6. Handoff is used only when responsibility moves to another agent or session.

Important gates remain separate:

```text
approve a draft != approve a work order
approve a work order != approve AFK delegation
approve code changes != approve commit or push
approve GitHub read != approve GitHub write
```

## Intake Existing Code

Use `intake-existing-code` to clarify work in an existing repository before planning
or implementation.

Good requests:

```text
Investigate why password reset emails are sent twice.
Clarify the scope of adding CSV export to the reports screen.
Inspect this repository and turn the caching improvement into an actionable task.
```

Typical interaction:

```text
User:
The API sometimes returns stale inventory. Help me understand and plan the fix.

Orchestrator:
Proposed workflow: intake-existing-code
Proposed agent: intake-agent
Missing context: affected endpoint, expected freshness, reproduction evidence
Next step: inspect non-sensitive project context and ask focused questions

User:
Continue with read-only inspection.
```

Expected outputs may include a clarified request, diagnosis draft, issue draft
candidate or work-order candidate. This workflow does not modify product code.

Common next routes:

```text
clarified requirement -> backlog-management
ready work order -> tdd-implementation
architecture-impacting change -> architecture-ddd
```

## Ideation From Zero

Use `ideation-from-zero` when starting from a product or system idea without an
approved Software Design Description.

Good requests:

```text
I want to design a lightweight booking platform for small studios.
Help me turn this idea for an offline-first field app into requirements.
Grill me about a product for managing recurring compliance reviews.
```

Typical interaction:

```text
User:
I want a service that lets teams approve expenses from chat.

Intake agent:
Who submits expenses, who approves them, and what result must be visible in chat?

User:
Employees submit them, managers approve them, and finance needs an audit trail.
```

The agent asks focused questions, separates facts from assumptions, and produces an
SDD draft with requirements, use cases, test cases and traceability.

Draft location:

```text
.factory/runs/<run-id>/artifacts/ideation/
```

Approved SDD location:

```text
docs/sdd/
```

The user must approve the SDD before routing to `architecture-ddd`.

## Architecture DDD

Use `architecture-ddd` after an SDD is approved and the system needs boundaries,
contracts, data design, ADRs or architecture-driven backlog planning.

Good requests:

```text
Design the architecture from the approved SDD in docs/sdd/.
Define bounded contexts and API contracts for this product.
Review the approved requirements and propose the simplest viable architecture.
```

Typical interaction:

```text
User:
Use architecture-ddd for the approved SDD. The backend is FastAPI with PostgreSQL.

Software architect:
I will begin with architecture-grill-me, then use DDD strategic design.
FastAPI and PostgreSQL stack guidance will be used only after versions and paths
are confirmed. Consequential decisions and promotion to docs require approval.
```

The architect selects only skills justified by confirmed questions. Possible outputs:

```text
architecture-questionnaire.md
architecture-overview.md
domain/context-map.md
bounded-contexts/
api/
data/
adrs/
optional self-contained HTML diagrams
integration-test-strategy.md
frontend/frontend-architecture.md
frontend/route-ownership-map.md
frontend/server-client-boundary-map.md
frontend/state-strategy.md
frontend/api-consumption-contract.md
frontend/test-strategy.md
frontend/security-boundary.md
```

When the system has a frontend, architecture is incomplete until it explains feature
ownership, routes, server/client execution boundaries, state ownership, API/error
consumption, session/security boundaries and frontend tests.

Drafts stay under `.factory/runs/<run-id>/artifacts/architecture/`. Promotion to
`docs/architecture/` or `docs/adr/` requires approval.

## Architecture Foundation

Use `architecture-foundation` after architecture and ADRs are approved, before
functional slices are delegated to the implementer.

Good requests:

```text
Materialize the approved architecture as a minimal executable foundation.
Create the approved FastAPI module boundaries and architecture tests, but no business logic.
Prepare the project structure and required contracts for the first vertical slice.
```

The foundation agent first produces an exact plan containing paths, required contracts,
known consumers, composition-root wiring, architecture tests, commands and exclusions.
The user must approve that plan and the product-structure write before files change.

Allowed output:

```text
minimal executable project structure
approved module and bounded-context boundaries
contracts required by known consumers or the first slices
minimal composition root
architecture and dependency-boundary tests
conformance report and first-slice backlog inputs
approved frontend route groups, layouts and public feature surfaces
frontend boundary tests and API-client boundary
```

Forbidden output:

```text
business rules
generic CRUD
complete repository adapters
future module placeholders
interfaces without known consumers
functional screens or speculative global state
```

Typical transition:

```text
architecture-ddd -> architecture-foundation -> backlog-management
                                  |
                                  -> tdd-implementation for approved functional slices
```

## Backlog Management

Use `backlog-management` to inspect, reconcile and manage local drafts and GitHub
issues, or to select a ready task for implementation.

Good requests:

```text
What is the current backlog, including GitHub issues and local drafts?
Which tasks are blocked or missing?
Recommend the next ready task and explain why.
Take issue 42 and prepare it for implementation.
```

Backlog status example:

```text
User:
Show the current backlog and tell me which tasks are ready.

Backlog manager:
Sources: local backlog drafts and read-only GitHub issues
Ready: 3
Needs refinement: 2
Blocked: 1
Recommended next task: GW-18, because it unlocks two dependent slices
Pending gates: none for this read-only snapshot
```

Task selection example:

```text
User:
Take GW-18.

Backlog manager:
GW-18 is ready. I prepared a work-order candidate with acceptance criteria,
path scopes, allowed commands and definition of done.
Pending gates:
1. Approve the exact work order.
2. Approve AFK delegation to implementer-agent.
```

The backlog manager may use governed GitHub CLI reads. Issue edits, comments,
assignment or creation require separate approval.

Key artifacts:

```text
.factory/runs/<run-id>/artifacts/backlog-management/backlog-snapshot.md
.factory/runs/<run-id>/artifacts/backlog-management/gap-analysis.md
.factory/runs/<run-id>/artifacts/backlog-management/task-selection.md
.factory/runs/<run-id>/artifacts/backlog-management/work-order-candidate.md
```

## Backlog Task Delivery

Use `backlog-task-delivery` for a compound request that starts with task selection
and ends with an independent verification decision.

Good requests:

```text
Buscame una tarea del backlog pendiente, implementalo y verificalo.
Find a pending backlog task, implement it and verify it.
Select the highest-priority ready GitHub issue, implement it and verify the result.
Choose a small unblocked local task and carry it through verification.
```

Typical interaction:

```text
User:
Buscame una tarea del backlog pendiente, implementalo y verificalo.

Orchestrator:
Proposed workflow: backlog-task-delivery
I will first perform read-only backlog discovery and select one ready task.
Before code changes I will show the exact work order and pause for:
1. Work-order approval.
2. AFK delegation approval.
GitHub writes and Git actions remain separately gated.
```

After both approvals, the orchestrator composes:

```text
    backlog-management -> tdd-implementation -> feature-pr-delivery -> verification-pr
```

The broad initial request does not approve the selected work order, AFK delegation,
scope changes, commits, pushes, PR creation or any GitHub write.

## TDD Implementation

Use `tdd-implementation` only after a complete work order and AFK delegation are
approved.

Required work-order fields:

```text
work_order_id
run_id
workflow_id
target_agent
objective
acceptance_criteria
path_scopes
allowed_commands
human_gates
definition_of_done
```

Start example:

```text
User:
Approve work order GW-18 as written and delegate it to implementer-agent.

Implementer:
Work order validated. I will execute one behavior-level RED/GREEN cycle at a time
inside the approved paths and commands. Dependency, scope, Git and remote actions
remain gated.
```

Implementation behavior:

1. Prepare a TDD plan.
2. Add or activate one observable behavior test.
3. Confirm RED fails for the expected reason.
4. Implement the smallest GREEN change.
5. Refactor only while green.
6. Run approved final checks.
7. Write evidence and hand off to verification.

When integration behavior matters, the implementer can use:

```text
integration-test-design
integration-testing
```

When the confirmed backend is FastAPI, it may also use:

```text
fastapi-backend-guidance
fastapi-performance
```

For a Next.js slice, the work order should also state:

```text
affected feature and route
Server/Client Component boundary
URL, server, local or global state ownership
API/error consumption contract
loading, empty, unauthorized and stale states
frontend behavior, accessibility and E2E tests
approved UI sources and shadcn/ui usage
responsive checks at 390, 1024 and 1440 CSS pixels
visual QA evidence
```

If these fields are missing, the frontend-bearing task is `needs_refinement` and
must not be delegated.

The workflow stops before dependency changes, scope changes, unknown commands,
destructive actions, commit, push, PR creation or deployment.

## Feature PR Delivery

Use `feature-pr-delivery` after local implementation checks pass.

```text
develop -> feature/<work-order-id>-<slug> -> PR to develop
        -> feature / regression-gate -> verifier -> squash merge to develop
```

Commit, push, PR creation, PR review, merge and branch deletion are separate gates.
When CI fails, the PR remains open with `ci_failed`; failures return to the implementer.
Every corrective push invalidates prior CI evidence and verifier approval.

## Verification PR

Use `verification-pr` after implementation or when asking for a review of an
implementation or PR.

Good requests:

```text
Verify the implementation for work order GW-18.
Review this PR against its acceptance criteria and TDD evidence.
Check whether the FastAPI integration tests prove the requested behavior.
```

Typical interaction:

```text
User:
Run verification-pr for GW-18.

Verifier:
I will review findings first, then scope, acceptance criteria, RED/GREEN evidence,
integration-test realism and policy compliance. I will not modify code.
```

Possible decisions:

```text
pass
changes_requested
needs_more_evidence
blocked_by_ci
blocked_by_branch_state
```

Missing or invalid RED/GREEN evidence should produce `needs_more_evidence`.
GitHub PR comments, commits, pushes, PR creation and merge remain separately gated.

## Release Promotion

Use `release-promotion` when verified changes in `develop` are ready for production.

```text
develop -> release PR to main -> release / full-regression-gate
        -> production approval -> merge to main -> production deployment
```

Feature branches must never target `main`. The release manager coordinates the release,
but does not repair code or bypass failed checks. Deployment verification must reference
the exact SHA merged into `main`.

Key artifacts:

```text
.factory/runs/<run-id>/artifacts/verification/verifier-report.md
.factory/runs/<run-id>/artifacts/verification/github-pr-comment.md
```

## End-To-End Examples

### New Product To Implementation

```text
1. "Help me define a new scheduling product."
   -> ideation-from-zero

2. "I approve the SDD. Design the architecture."
   -> architecture-ddd

3. "Materialize the approved architecture without business logic."
   -> architecture-foundation

4. "Show the resulting backlog and recommend the first tracer task."
   -> backlog-management

5. "Approve the work order and delegate it."
   -> tdd-implementation

6. "Deliver the feature PR through CI and verification."
   -> feature-pr-delivery and verification-pr

7. "Promote verified develop state to production."
   -> release-promotion
```

### Existing Bug To Verified Fix

```text
1. "Investigate duplicate order creation."
   -> intake-existing-code

2. "Prepare the diagnosed task and select it."
   -> backlog-management

3. "Approve and delegate the work order."
   -> tdd-implementation

4. "Verify the regression test and implementation."
   -> verification-pr
```

### Backlog Review Without Code Changes

```text
User:
Read local drafts and GitHub issues. Which work is ready, what is blocked, and what
approved requirement has no backlog task?

Result:
backlog-management produces a read-only snapshot and gap analysis. It does not
delegate or write to GitHub unless separately requested and approved.
```

### Select, Implement And Verify One Backlog Task

```text
1. "Find a pending backlog task, implement it and verify it."
   -> backlog-task-delivery starts with read-only discovery

2. Gridwork presents the selected task and exact work order.
   -> user approves the work order and AFK delegation

3. Gridwork implements through TDD and runs approved checks.
   -> tdd-implementation

4. Gridwork independently reviews evidence and acceptance criteria.
   -> verification-pr produces pass, changes_requested or needs_more_evidence
```

## Useful Approval Phrases

Approvals should name the exact action and scope.

Good:

```text
Approve read-only GitHub issue discovery for owner/repo.
Approve promotion of these architecture drafts to docs/architecture/.
Approve this architecture foundation plan and its exact product-structure writes.
Approve work order GW-18 exactly as written.
Approve AFK delegation of GW-18 to implementer-agent.
Approve creating GitHub issues from drafts GW-21 and GW-22.
Approve staging only the listed files.
Approve push of feature/GW-18-create-todo.
Approve creation of the feature PR targeting develop.
Approve squash merge of PR 42 into develop.
Approve creation of the develop-to-main release PR.
Approve production promotion and merge to main.
```

Too broad:

```text
Do everything.
Use GitHub as needed.
Make any changes required.
```

## Troubleshooting

If routing is wrong, say:

```text
Stop. Re-evaluate the request and explain the proposed workflow before acting.
```

If a workflow is blocked, ask:

```text
List the exact missing inputs, unresolved decisions and approval gates.
```

If an agent proposes an unexpected side effect, do not approve it until the action,
scope and target are explicit.

## Monorepo Bootstrap And Delivery Infrastructure

Use this order for a new monorepo:

```text
architecture-ddd
-> repository-bootstrap
-> architecture-foundation
-> delivery-infrastructure
-> backlog-management
-> tdd-implementation
-> feature-pr-delivery
-> verification-pr
```

`repository-bootstrap` creates approved framework roots, root quality commands,
containers and Compose environment overlays. It may add minimal health or wiring
probes, but it does not implement business behavior.

`architecture-foundation` then materializes the approved domain boundaries,
contracts, composition root and architecture tests inside that repository skeleton.

`delivery-infrastructure` creates reusable GitHub Actions and plans required checks:

```text
feature / regression-gate
develop / integration-gate
release / full-regression-gate
production / smoke-gate
```

Use `ci-failure-repair` when a required PR check fails. The workflow diagnoses the
current head SHA, prepares the smallest repair handoff, and returns to verifier only
after the new SHA is green.

Example:

```text
Bootstrap the approved Next.js and FastAPI monorepo, create Compose environments,
and create the GitHub Actions required by Gridwork delivery workflows.
```
