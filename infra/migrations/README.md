# Migration Contract

`0000-foundation.sql` proves that the one-shot `migrate` service can connect and fail
closed before API and worker readiness.

It creates no tables, extensions, roles, RLS policies or functional schema. Future
migrations must be introduced by approved TDD work orders and remain backward
compatible during the rollback window.

