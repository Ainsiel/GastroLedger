# Agent Permissions Policy

## Rule

```text
default = deny
skills_raise_permissions = false
most_restrictive_rule_wins = true
```

## Agent Profiles

### orchestrator-full-v1

Can read `.gridwork/`, policies, manifests and non-sensitive project context. Can write `.factory/` runtime artifacts. Cannot implement product code.

### intake-hitl

Can read non-sensitive project context and write local drafts. Cannot implement code or publish issues.

### architect-hitl

Can write architecture drafts and approved architecture docs. Can use stack skills for design guidance after technology detection. Cannot implement product code.

### architecture-foundation-hybrid

Can write only the approved minimal project structure, required boundary contracts,
composition root and architecture tests. Cannot implement business behavior or invent
architecture. Foundation plans, product-structure writes and scope changes require gates.

### planner-assisted

Can create local issue drafts and publish plans. GitHub writes require approval.

### backlog-manager-assisted

Can read local backlog artifacts and governed GitHub issue data, write backlog reports,
prepare work order candidates and handoffs. GitHub writes, work-order approval and AFK
delegation require separate approval.

### implementer-afk-tdd

Can modify scoped product, test and infrastructure files only when an approved work order exists. May use confirmed stack skills. Must follow TDD and command allowlists.

### verifier-assisted-readonly

Can inspect code and evidence, use stack skills in review mode, run allowlisted checks and write reports. Cannot modify code in v1.

### release-manager-hybrid

Can inspect release scope, PRs, checks and deployment evidence. Can prepare and execute
approved release PR, merge and deployment-observation actions. Cannot implement code,
bypass checks or access secret values.

### platform-assisted

Can write approved repository scaffolds, `.github/`, containers, Compose, root quality commands and platform documentation. Cannot implement business behavior. Remote GitHub changes and deployment require approval.

## Remote Actions

GitHub writes, branch push, PR creation, merge, release creation and deploy require
explicit approval. Only authorized delivery workflows may execute approved merges.
