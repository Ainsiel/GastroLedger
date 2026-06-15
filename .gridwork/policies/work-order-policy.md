# Work Order Policy

An AFK implementation requires an approved work order containing:

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
base_branch
feature_branch
target_branch
required_local_checks
required_pr_checks
```

If a required field is missing, set:

```text
status = blocked
blocked_reason = missing_work_order_contract
```

The work order cannot expand permissions, override policies or authorize GitHub writes implicitly.

## Frontend Work Orders

When the work order has frontend scope, it must also contain:

```text
affected_frontend_feature_and_route
approved_ui_sources
selected_frontend_skills
server_client_boundary
frontend_state_ownership
api_error_consumption_contract
applicable_visible_states
responsive_viewports
accessibility_expectations
frontend_test_evidence
visual_qa_evidence
```

If any applicable field is missing, set:

```text
status = blocked
blocked_reason = missing_frontend_delivery_contract
```
