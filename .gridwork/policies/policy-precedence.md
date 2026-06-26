# Policy Precedence

## Order

```text
user_instruction_for_current_task
system_or_tool_safety_rules
repository_policy
workflow_contract
agent_contract
skill_contract
stack_pack_guidance
work_order
```

## Conflict Rule

```text
deny_by_default = true
most_restrictive_rule_wins = true
skill_permissions_inherited_only = true
stack_pack_guidance_is_not_permission = true
```

If two policies disagree and the safe action is unclear, stop and ask.

