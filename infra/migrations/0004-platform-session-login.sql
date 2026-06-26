\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gastroledger_session_manager') THEN
        CREATE ROLE gastroledger_session_manager NOLOGIN NOSUPERUSER NOBYPASSRLS;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO gastroledger_session_manager;
GRANT SELECT ON
    platform_tenants,
    platform_users,
    platform_memberships
TO gastroledger_session_manager;
GRANT SELECT, INSERT, UPDATE ON platform_sessions TO gastroledger_session_manager;
GRANT gastroledger_session_manager TO :"runtime_user";

DROP POLICY IF EXISTS platform_tenants_session_manager ON platform_tenants;
CREATE POLICY platform_tenants_session_manager ON platform_tenants
FOR SELECT
USING (current_user = 'gastroledger_session_manager');

DROP POLICY IF EXISTS platform_users_session_manager ON platform_users;
CREATE POLICY platform_users_session_manager ON platform_users
FOR SELECT
USING (current_user = 'gastroledger_session_manager');

DROP POLICY IF EXISTS platform_memberships_session_manager ON platform_memberships;
CREATE POLICY platform_memberships_session_manager ON platform_memberships
FOR SELECT
USING (current_user = 'gastroledger_session_manager');

DROP POLICY IF EXISTS platform_sessions_session_manager ON platform_sessions;
CREATE POLICY platform_sessions_session_manager ON platform_sessions
USING (current_user = 'gastroledger_session_manager')
WITH CHECK (current_user = 'gastroledger_session_manager');

COMMIT;
