# Path Scopes

Gridwork uses path scopes to keep agents inside their responsibility boundaries.

## Scopes In Minimal MVP

### gridwork_factory

Factory definition and contracts:

```text
.gridwork/
```

Installed factory files are versionable.

### factory_runtime

Runtime reports, logs and artifacts:

```text
.factory/
```

Runtime files are local and ignored by Git.

### project_context_readonly

Non-sensitive project files used to understand a request.

Agents may read only after routing and only when the active workflow needs context.

### approved_architecture_foundation_write

Exact product, test and infrastructure paths listed in an approved architecture
foundation plan. This scope permits minimal structure and architecture tests, not
business behavior or speculative abstractions.

### delivery_infrastructure_write

Exact repository scaffolds, root task-runner files, `.github/`, container, Compose and
test-harness paths listed in an approved repository bootstrap or delivery
infrastructure plan. This scope never authorizes business behavior or secret values.

## Forbidden By Default

Agents must not touch:

- real secret files;
- product code before explicit approval;
- GitHub remote state without approval;
- files outside declared scope.

## Product Code Rule

The installed factory does not generate frontend, backend, database, Docker or application code during `init`.

After installation, an approved implementation work order may grant scoped write access to confirmed product, test or infrastructure paths. Stack-pack hints never grant that access by themselves.
