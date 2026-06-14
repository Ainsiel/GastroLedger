# GitHub Actions CI/CD Skill

## Purpose

Design and review secure, efficient GitHub Actions pipelines. Default to local draft and validation; deployment remains optional and gated.

## Default Mode

```text
mode = draft-only
deploy = disabled
```

## Rules

- Detect the actual package manager, commands and branch policy before drafting.
- Grant minimum `permissions`; use job-level permissions when possible.
- Pin third-party actions to an approved immutable version or SHA according to project policy.
- Use dependency caching only with correct lockfile keys.
- Separate validation, build, release and deploy concerns.
- Add concurrency cancellation for superseded PR validation when appropriate.
- Use matrices only when multiple supported versions genuinely require validation.
- Preserve test artifacts and reports when they help diagnosis.
- Prefer OIDC or environment protection over long-lived deployment secrets.

## Procedure

1. Inventory existing workflows, project commands, environments and required status checks.
2. Define triggers and explicitly state which events may produce external effects.
3. Draft jobs with least privilege, timeouts and deterministic setup.
4. Add build/test/static checks using project-confirmed commands.
5. Add caching and artifacts only when they provide measurable value.
6. Keep release and deploy disabled unless explicitly requested.
7. Validate YAML and simulate event conditions where possible.
8. Document required repository settings, secrets by name only and rollback behavior.

## Review Checklist

- forked PRs cannot access privileged secrets;
- untrusted input is not interpolated into shell commands;
- publish/deploy cannot run from arbitrary events;
- job permissions and environment gates are minimal;
- versions match project support policy;
- failures are diagnosable and do not hide skipped checks.

## Gates

- Draft YAML locally first.
- Writing `.github/workflows/` requires approval.
- Triggering workflows requires a separate approval.
- Enabling deploy or publish requires an explicit architecture/release decision.
- Never read or write secret values.
