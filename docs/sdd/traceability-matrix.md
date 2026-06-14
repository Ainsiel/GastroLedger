# Traceability Matrix

## Functional Requirements To Use Cases

| Requirement | Use cases |
|---|---|
| FR-001, FR-002 | UC-001, UC-002 |
| FR-003, FR-028 | UC-003 |
| FR-004 | UC-004 |
| FR-005 | UC-005 |
| FR-006 | UC-006 |
| FR-007 | UC-008 |
| FR-008, FR-009 | UC-009 |
| FR-010, FR-031 | UC-010 |
| FR-011 | UC-007 |
| FR-012 | UC-012 |
| FR-013 | UC-013 |
| FR-014 | UC-014 |
| FR-015 | UC-011 |
| FR-016 | UC-015, UC-016, UC-017 |
| FR-017 | UC-018 |
| FR-018, FR-029 | UC-019 |
| FR-019 | UC-020 |
| FR-020 | UC-011, UC-013, UC-014, UC-016, UC-017, UC-018, UC-020, UC-021 |
| FR-021, FR-022, FR-030 | UC-021 |
| FR-023 | UC-022 |
| FR-024 | UC-023 |
| FR-025 | UC-024 |
| FR-026 | UC-025 |
| FR-027 | UC-002, UC-003, UC-012, UC-013, UC-014, UC-015, UC-016, UC-017, UC-018, UC-020, UC-022, UC-023, UC-024 |
| FR-032 | Architecture export contract; acceptance deferred to foundation backlog |

## Use Cases To Tests

Every `UC-NNN` maps to `TC-NNN-S`, `TC-NNN-A` and `TC-NNN-F`. The exact flow
identifier is recorded in `test-cases.md`, allowing automated completeness checks.

## Quality Attribute Verification

| Quality attribute | Primary evidence |
|---|---|
| QA-001 | Cross-tenant integration and RLS tests |
| QA-002 | Ledger constraint, concurrency and invariant tests |
| QA-003, QA-006 | Worker integration tests and performance baseline |
| QA-004 | CSV idempotency and partial-result tests |
| QA-005 | Dashboard query performance baseline |
| QA-007, QA-008 | Availability monitoring contract and restore rehearsal |
| QA-009, QA-010 | Authorization and audit atomicity tests |
| QA-011 | Frontend accessibility and end-to-end checks |
| QA-012 | Architecture conformance tests |
| QA-013 | Isolated Compose integration environment |
| QA-014 | Tenant export acceptance and restore/import rehearsal |
