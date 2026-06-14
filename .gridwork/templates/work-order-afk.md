---
work_order_id: <YYYYMMDD-HHMM-slug>
run_id: <run-id>
workflow: tdd-implementation
agent: implementer-agent
status: draft
source_issue: <github-url-or-local-draft>
approved_by_user: false
base_branch: develop
feature_branch: feature/<work-order-id>-<slug>
target_branch: develop
---

# AFK Work Order

## Goal

<goal>

## Scope

<allowed files and behavior>

## Path Scopes

- <confirmed path>

## Acceptance Criteria

- [ ] <criterion>

## Allowed Commands

- `<confirmed command>`

## Delivery Contract

- Required local checks:
- Required PR checks: `feature / regression-gate`
- Expected CI workflow:
- Merge strategy: squash
- Branch cleanup policy:

## TDD Plan

### Red

<first failing test>

### Green

<minimal implementation>

### Refactor

<cleanup constraints>

## Gates

- dependency_change
- scope_change
- unknown_command
- github_write
- create_commit
- push_branch
- create_pr
- merge_to_develop
- secret_value_needed

## Definition Of Done

- [ ] Acceptance criteria are satisfied.
- [ ] RED and GREEN evidence is recorded.
- [ ] Allowlisted final checks pass.
- [ ] Implementation summary and verifier handoff are ready.
