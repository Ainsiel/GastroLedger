# Migration Contract

`0000-foundation.sql` proves that the one-shot `migrate` service can connect and fail
closed before API and worker readiness.

It creates no tables, extensions, roles, RLS policies or functional schema.
`0001-platform-registration.sql` is the first approved functional migration and
contains only the minimum GL-001 registration, local-session and denial-audit
relations. Future migrations must remain backward compatible during the rollback
window.

