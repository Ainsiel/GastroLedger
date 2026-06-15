\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gastroledger_app') THEN
        CREATE ROLE gastroledger_app NOLOGIN NOSUPERUSER NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gastroledger_registration') THEN
        CREATE ROLE gastroledger_registration NOLOGIN NOSUPERUSER NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gastroledger_session_resolver') THEN
        CREATE ROLE gastroledger_session_resolver NOLOGIN NOSUPERUSER NOBYPASSRLS;
    END IF;
END
$$;

SELECT format(
    'CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS PASSWORD %L',
    :'runtime_user',
    :'runtime_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'runtime_user')
\gexec

SELECT format(
    'ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS PASSWORD %L',
    :'runtime_user',
    :'runtime_password'
)
\gexec

CREATE TABLE IF NOT EXISTS platform_tenants (
    id uuid PRIMARY KEY,
    slug text NOT NULL UNIQUE,
    name text NOT NULL,
    status text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS platform_tenant_settings (
    tenant_id uuid PRIMARY KEY REFERENCES platform_tenants(id),
    locale text NOT NULL DEFAULT 'en',
    base_currency text NOT NULL DEFAULT 'USD'
);
CREATE TABLE IF NOT EXISTS platform_users (
    id uuid PRIMARY KEY,
    normalized_login text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS platform_memberships (
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    user_id uuid NOT NULL REFERENCES platform_users(id),
    role text NOT NULL,
    PRIMARY KEY (tenant_id, user_id)
);
CREATE TABLE IF NOT EXISTS platform_branches (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    code text NOT NULL,
    name text NOT NULL,
    UNIQUE (tenant_id, code)
);
CREATE TABLE IF NOT EXISTS platform_sessions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    user_id uuid NOT NULL REFERENCES platform_users(id),
    token_hash text NOT NULL UNIQUE,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT platform_sessions_membership_fk
        FOREIGN KEY (tenant_id, user_id)
        REFERENCES platform_memberships (tenant_id, user_id)
        ON DELETE CASCADE
);
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'platform_sessions_membership_fk'
          AND conrelid = 'platform_sessions'::regclass
    ) THEN
        ALTER TABLE platform_sessions
        ADD CONSTRAINT platform_sessions_membership_fk
        FOREIGN KEY (tenant_id, user_id)
        REFERENCES platform_memberships (tenant_id, user_id)
        ON DELETE CASCADE;
    END IF;
END
$$;
CREATE TABLE IF NOT EXISTS control_audit_events (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    actor_id uuid NOT NULL REFERENCES platform_users(id),
    correlation_id text NOT NULL,
    action text NOT NULL,
    object_reference text NOT NULL,
    occurred_at timestamptz NOT NULL DEFAULT now()
);

GRANT USAGE ON SCHEMA public TO gastroledger_app;
GRANT SELECT ON
    platform_tenants,
    platform_tenant_settings,
    platform_memberships
TO gastroledger_app;
GRANT INSERT ON control_audit_events TO gastroledger_app;
GRANT USAGE ON SCHEMA public TO gastroledger_registration;
GRANT INSERT ON
    platform_tenants,
    platform_tenant_settings,
    platform_users,
    platform_memberships,
    platform_branches,
    platform_sessions
TO gastroledger_registration;
GRANT USAGE ON SCHEMA public TO gastroledger_session_resolver;
GRANT SELECT ON platform_sessions TO gastroledger_session_resolver;
GRANT
    gastroledger_app,
    gastroledger_registration,
    gastroledger_session_resolver
TO :"runtime_user";

ALTER TABLE platform_tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_tenants FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_tenant_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_tenant_settings FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_users FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_memberships FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_branches FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE control_audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_audit_events FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS platform_tenants_scope ON platform_tenants;
CREATE POLICY platform_tenants_scope ON platform_tenants
USING (
    id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);
DROP POLICY IF EXISTS platform_users_registration ON platform_users;
CREATE POLICY platform_users_registration ON platform_users
USING (current_user = 'gastroledger_registration')
WITH CHECK (current_user = 'gastroledger_registration');
DROP POLICY IF EXISTS platform_tenant_settings_scope ON platform_tenant_settings;
CREATE POLICY platform_tenant_settings_scope ON platform_tenant_settings
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);
DROP POLICY IF EXISTS platform_memberships_scope ON platform_memberships;
CREATE POLICY platform_memberships_scope ON platform_memberships
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);
DROP POLICY IF EXISTS platform_branches_scope ON platform_branches;
CREATE POLICY platform_branches_scope ON platform_branches
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);
DROP POLICY IF EXISTS platform_sessions_scope ON platform_sessions;
CREATE POLICY platform_sessions_scope ON platform_sessions
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user IN ('gastroledger_registration', 'gastroledger_session_resolver')
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);
DROP POLICY IF EXISTS control_audit_events_scope ON control_audit_events;
CREATE POLICY control_audit_events_scope ON control_audit_events
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);

COMMIT;
