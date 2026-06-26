# Gridwork Factory

Gridwork installed a software factory in this repository. It did not generate product code.

This folder contains the factory contracts that an agent can read by chat:

- `factory.json` declares the installed factory profile.
- `agents/` contains agent manifests and contracts.
- `workflows/` contains workflow playbooks.
- `skills/` contains reusable skills.
- `policies/` contains rules for paths, logging, secrets and GitHub CLI.
- `stack-packs/` contains composable stack guidance and approved bootstrap skills.
- `schemas/` contains versioned JSON contracts.
- `templates/` contains report templates used by `init` and future runs.
- `docs/` contains installed catalogs for agents, workflows, skills and the active factory profile.

Runtime reports live in `.factory/` at the repository root. That folder is local runtime state and should stay ignored by Git.

Start with `QUICKSTART.md`. There is no `gridwork run` command in v1.
Use `docs/WORKFLOW_GUIDE.md` for practical workflow examples and approval guidance.

The full profile includes a backlog manager for local/GitHub backlog questions and
task selection, an architecture foundation agent for approved executable structure,
a release manager for governed production promotion, and technology-agnostic
integration and frontend architecture guidance.
