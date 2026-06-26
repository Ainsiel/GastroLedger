# Gridwork Release Publisher

## Purpose

Prepare Gridwork factory releases and CLI release plans.

Default mode is dry-run and plan-only. The skill must not create tags, push tags, create GitHub Releases, upload assets, merge branches or publish npm packages unless the user gives explicit approval for the exact remote action.

## Modes

```text
factory-release
cli-release
```

`factory-release` prepares GitHub Release assets for the factory.

`cli-release` prepares npm CLI release plans for GitHub Actions. It does not run `npm publish`.

## Inputs

- Target factory version, SemVer.
- GitHub source in `owner/repo` format.
- Source commit.
- Prerelease approval when the version is a prerelease.
- Factory source directory, default `factory/.gridwork`.
- CLI package ownership confirmation when using `cli-release`.
- Official factory source confirmation when using `cli-release`.

## Allowed Actions

- Read `factory/.gridwork/`.
- Validate factory manifests and release bundle paths.
- Generate release artifacts in `.factory/runs/<run-id>/artifacts/release/`.
- Generate:
  - `gridwork-factory-v<version>.zip`;
  - `gridwork-factory-v<version>.manifest.json`;
  - `gridwork-factory-v<version>.sha256`;
  - `gridwork-factory-v<version>.release-notes.md`;
  - `factory-release-plan.md`;
  - `publish-commands.md`;
  - `factory-release-validation.json`.
- Prepare commands for human review.
- Generate CLI release artifacts:
  - `cli-release-plan.md`;
  - `cli-release-notes.md`;
  - `cli-npm-pack-report.md`;
  - `cli-release-validation.json`;
  - `cli-publish-commands.md`.

## Forbidden Actions

- Do not execute `git tag` without explicit approval.
- Do not execute `git push` without explicit approval.
- Do not execute `gh release create` without explicit approval.
- Do not upload assets without explicit approval.
- Do not overwrite or reuse a published tag or release.
- Do not publish npm.
- Do not run local `npm publish`.
- Do not merge branches.
- Do not include `.factory/`, `.git/`, `node_modules/`, `.docs/`, `docs/`, `packages/`, `dist/`, product code folders or secret-like files in the bundle.

## Canonical Contract

Use factory release tags:

```text
factory-v<version>
```

Use assets:

```text
gridwork-factory-v<version>.zip
gridwork-factory-v<version>.manifest.json
gridwork-factory-v<version>.sha256
gridwork-factory-v<version>.release-notes.md
```

The bundle root must be `.gridwork/`.

Use CLI release tags:

```text
cli-v<version>
```

CLI stable releases use npm dist-tag `latest`.

CLI prereleases use npm dist-tag `next`.

## Workflow

1. Confirm the release mode, version and source.
2. Run the dry-run release preparation.
3. Review `factory-release-validation.json`.
4. Verify the generated bundle can be installed by `gridwork init`.
5. Review `publish-commands.md`.
6. Stop at the approval gate before any remote command.

## Recommended Factory Command

```bash
gridwork release factory --dry-run --factory-version <version> --source <owner/repo> --source-commit <sha>
```

For prereleases:

```bash
gridwork release factory --dry-run --factory-version <version-prerelease> --source <owner/repo> --source-commit <sha> --allow-prerelease
```

## Recommended CLI Command

```bash
gridwork release cli --dry-run --source <owner/repo> --source-commit <sha> --confirm-package-ownership --confirm-official-source
```

## Output Rule

Every run must leave local evidence under `.factory/runs/<run-id>/artifacts/release/`.

The skill must report clearly:

- whether publishing was executed;
- which assets were generated;
- which commands require approval;
- which blockers prevent release.
