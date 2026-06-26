# Security Policy

## Core Rule

Agents must not read, print, store or publish real secret values.

## Secret Files

Do not read values from:

- `.env`
- `.env.*`
- `*.pem`
- `*.key`
- `*.p12`
- `*.pfx`
- `credentials.json`
- `secrets.json`
- `service-account*.json`

Allowed references:

- `.env.example`
- `.env.template`
- `.env.sample`
- `example.env`
- sanitized user-provided summaries

## Redaction

Redact suspicious values before writing logs or reports:

- authorization headers;
- tokens;
- passwords;
- API keys;
- private keys;
- connection strings with credentials.

Use placeholders such as:

```text
[REDACTED:secret]
[REDACTED:token]
[REDACTED:connection-string]
```

## GitHub

GitHub tokens are used only by the user's environment or approved tools. Gridwork reports must never write `GITHUB_TOKEN`, `GH_TOKEN` or their values.
