\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS platform_warehouses (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    branch_id uuid NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    type text NOT NULL CHECK (type IN ('kitchen', 'bar', 'general')),
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    UNIQUE (branch_id, code),
    CONSTRAINT platform_warehouses_branch_tenant_fk
        FOREIGN KEY (branch_id, tenant_id)
        REFERENCES platform_branches (id, tenant_id)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'platform_warehouses_branch_tenant_fk'
          AND conrelid = 'platform_warehouses'::regclass
    ) THEN
        ALTER TABLE platform_warehouses
        ADD CONSTRAINT platform_warehouses_branch_tenant_fk
        FOREIGN KEY (branch_id, tenant_id)
        REFERENCES platform_branches (id, tenant_id);
    END IF;
END
$$;

GRANT SELECT, INSERT, UPDATE ON platform_warehouses TO gastroledger_app;

ALTER TABLE platform_warehouses ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_warehouses FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS platform_warehouses_scope ON platform_warehouses;
CREATE POLICY platform_warehouses_scope ON platform_warehouses
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
