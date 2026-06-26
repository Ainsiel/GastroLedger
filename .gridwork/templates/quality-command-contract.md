# Root Quality Command Contract

| Command | Required behavior |
|---|---|
| `make lint` | Lint every selected component. |
| `make unit-test` | Run unit tests. |
| `make integration-test` | Run integration tests against isolated dependencies. |
| `make e2e-test` | Run end-to-end tests. |
| `make build` | Produce all deployable artifacts. |
| `make compose-validate` | Validate base and environment Compose combinations. |
| `make ci` | Run the local full regression contract. |

Equivalent task runners are allowed when these stable intents remain available from the repository root.
