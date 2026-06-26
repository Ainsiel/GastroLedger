# Security, Secrets And Redaction

## Rules

- Do not read real secret values.
- Use examples, templates or sanitized values.
- Do not write tokens, credentials or auth output into `.factory/`.
- Redact sensitive values in reports and comments.
- Never include `.env`, secret-like files or local caches in release bundles.

## Redaction Marker

Use:

```text
<redacted>
```

Do not include partial tokens.

