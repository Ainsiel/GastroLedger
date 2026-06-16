\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS platform_membership_roles (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    user_id uuid NOT NULL REFERENCES platform_users(id),
    role text NOT NULL,
    scope text NOT NULL,
    branch_id uuid,
    CONSTRAINT platform_membership_roles_membership_fk
        FOREIGN KEY (tenant_id, user_id)
        REFERENCES platform_memberships (tenant_id, user_id)
        ON DELETE CASCADE,
    CONSTRAINT platform_membership_roles_branch_fk
        FOREIGN KEY (branch_id, tenant_id)
        REFERENCES platform_branches (id, tenant_id),
    CONSTRAINT platform_membership_roles_scope_check
        CHECK (
            (scope = 'tenant' AND branch_id IS NULL)
            OR (scope = 'branch' AND branch_id IS NOT NULL)
        )
);

CREATE TABLE IF NOT EXISTS platform_invitations (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    invitee_login text NOT NULL,
    token_hash text NOT NULL UNIQUE,
    role text NOT NULL,
    scope text NOT NULL,
    branch_id uuid,
    created_by uuid NOT NULL REFERENCES platform_users(id),
    expires_at timestamptz NOT NULL,
    accepted_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT platform_invitations_branch_fk
        FOREIGN KEY (branch_id, tenant_id)
        REFERENCES platform_branches (id, tenant_id),
    CONSTRAINT platform_invitations_scope_check
        CHECK (
            (scope = 'tenant' AND branch_id IS NULL)
            OR (scope = 'branch' AND branch_id IS NOT NULL)
        )
);

INSERT INTO platform_membership_roles (id, tenant_id, user_id, role, scope, branch_id)
SELECT gen_random_uuid(), tenant_id, user_id, role, 'tenant', NULL
FROM platform_memberships
WHERE role = 'tenant_admin'
  AND NOT EXISTS (
      SELECT 1
      FROM platform_membership_roles existing
      WHERE existing.tenant_id = platform_memberships.tenant_id
        AND existing.user_id = platform_memberships.user_id
        AND existing.role = platform_memberships.role
        AND existing.scope = 'tenant'
  );

GRANT SELECT, INSERT ON platform_membership_roles TO gastroledger_app;
GRANT SELECT, INSERT, UPDATE ON platform_invitations TO gastroledger_app;
GRANT INSERT ON platform_users, platform_memberships, platform_sessions TO gastroledger_app;
GRANT INSERT ON control_audit_events TO gastroledger_registration;
GRANT SELECT ON platform_tenants TO gastroledger_registration;
GRANT SELECT, INSERT ON platform_membership_roles TO gastroledger_registration;
GRANT SELECT, INSERT, UPDATE ON platform_invitations TO gastroledger_registration;

ALTER TABLE platform_membership_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_membership_roles FORCE ROW LEVEL SECURITY;
ALTER TABLE platform_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_invitations FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS platform_membership_roles_scope ON platform_membership_roles;
CREATE POLICY platform_membership_roles_scope ON platform_membership_roles
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);

DROP POLICY IF EXISTS platform_invitations_scope ON platform_invitations;
CREATE POLICY platform_invitations_scope ON platform_invitations
USING (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
)
WITH CHECK (
    tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid
    OR current_user = 'gastroledger_registration'
);

COMMIT;
