# GitHub Issue Publisher Skill

## Purpose

Publish reviewed local issue drafts to GitHub in controlled, auditable batches.

## Preflight

Before preparing a command, verify:

- each draft is marked ready and approved;
- repository target is confirmed;
- title, body, acceptance criteria and labels are present;
- label audit passes;
- dependencies and duplicate risk were reviewed;
- the batch size and exact side effects are clear.

## Procedure

1. Build a publish plan mapping local draft IDs to intended GitHub issues.
2. Render exact sanitized titles, bodies, labels and commands.
3. Group a small coherent batch.
4. Ask for approval naming repository and exact drafts.
5. Execute only approved `gh issue create` commands.
6. Capture URLs and sanitized results.
7. Stop the batch on unexpected errors or remote state.
8. Write a publish report and preserve failed drafts for retry.

## Idempotency

- Search for an existing published URL or matching issue before retry.
- Never create a duplicate merely because the first result was uncertain.
- Do not edit an existing issue unless that edit is separately approved.

## Forbidden

- Do not create issues from unreviewed drafts.
- Do not invent labels.
- Do not create missing labels implicitly; use `github-label-manager`.
- Do not delegate AFK work automatically after publishing.
- Do not continue after partial failure without reviewing remote state.

## Forbidden

- Do not create issues from unreviewed drafts.
- Do not invent labels.
- Do not create missing labels implicitly; use `github-label-manager` with a separate approval.
- Do not delegate AFK work automatically after publishing.
