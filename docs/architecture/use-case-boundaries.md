# Use-Case Boundaries

```text
HTTP request -> transport mapping -> command/query -> application interactor
interactor -> authorization + domain policy + owned ports -> result/error
result/error -> transport mapping -> HTTP response
```

## Contract Before Behavior

Before implementation, each use case receives:

- typed input command or query;
- typed result and stable error categories;
- application interactor protocol;
- declared authorization policy;
- transaction and audit expectations;
- repository/service ports only for real boundaries;
- API contract and test locations.

Foundation creates signatures and module boundaries, not business behavior.

## Transaction Rules

- One state-changing command is one application transaction.
- Inventory-affecting commands create one immutable inventory transaction.
- Cross-context asynchronous facts are appended to outbox in the same transaction.
- Queries never mutate business state.
- Protected actions append audit evidence atomically where failure must block change.

## Error Contract

| Category | Meaning | HTTP |
|---|---|---|
| `validation_error` | Invalid transport or domain input | 422 |
| `authentication_required` | Missing or invalid local session | 401 |
| `forbidden` | Actor lacks tenant/branch policy | 403 |
| `not_found` | Resource absent or intentionally hidden | 404 |
| `conflict` | State, version, duplicate or stock conflict | 409 |
| `unprocessable_exception` | Valid request requires operator resolution | 422 |
| `rate_limited` | Local abuse threshold exceeded | 429 |
| `internal_error` | Unexpected fault with correlation ID | 500 |
