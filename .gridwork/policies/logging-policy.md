# Logging Policy

## Model

Operational traceability is local and file-based.

```text
.factory/runs/<run-id>/
```

Use:

- JSON for current state;
- JSONL for append-only events and tool calls;
- Markdown for human summaries and reports.

## Do Not Log

- secret values;
- full environment dumps;
- complete command output when it may contain sensitive data;
- private credentials;
- cookies or authorization headers.

## Minimum Event Types

When a run exists, record important events such as:

- `run.started`
- `workflow.selected`
- `skill.used`
- `approval.requested`
- `artifact.created`
- `run.blocked`
- `run.completed`

## Local Only

Runtime logs and reports stay in `.factory/` unless the user explicitly approves another destination.
