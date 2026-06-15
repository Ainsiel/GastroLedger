\set ON_ERROR_STOP on

BEGIN;

ALTER TABLE platform_tenant_settings
ADD COLUMN IF NOT EXISTS branch_limit integer NOT NULL DEFAULT 1;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'platform_tenant_settings_branch_limit_check'
          AND conrelid = 'platform_tenant_settings'::regclass
    ) THEN
        ALTER TABLE platform_tenant_settings
        ADD CONSTRAINT platform_tenant_settings_branch_limit_check
        CHECK (branch_limit BETWEEN 1 AND 100);
    END IF;
END
$$;

GRANT SELECT, UPDATE ON platform_tenant_settings TO gastroledger_app;
GRANT SELECT, INSERT ON platform_branches TO gastroledger_app;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'platform_branches_id_tenant_unique'
          AND conrelid = 'platform_branches'::regclass
    ) THEN
        ALTER TABLE platform_branches
        ADD CONSTRAINT platform_branches_id_tenant_unique UNIQUE (id, tenant_id);
    END IF;
END
$$;

COMMIT;
