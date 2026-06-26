# Compose Environment Plan

```text
base = infra/compose/compose.yaml
develop_overlay = infra/compose/compose.develop.yaml
qa_overlay = infra/compose/compose.qa.yaml
production_overlay = infra/compose/compose.production.yaml
optional_profiles = observability, migrations, testing
```

Document services, health checks, volumes, ports, dependency conditions, secret sources and validation commands.
