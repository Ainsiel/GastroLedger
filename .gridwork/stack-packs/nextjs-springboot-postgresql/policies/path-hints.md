# Path Hints

These are candidates, not rules.

```text
frontend = apps/web, frontend, web, client
backend = apps/api, backend, api, server
fastapi = apps/api, backend, api, server, src
db = db, infra/db, migrations
compose = infra/compose/compose.yaml, docker-compose.yml, compose.yml, infra/docker-compose.yml
```

The orchestrator must detect or ask before using a path as scope.
