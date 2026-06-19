\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS menu_item_branch_prices (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    recipe_version_id uuid NOT NULL,
    branch_id uuid NOT NULL,
    price numeric(24, 10) NOT NULL CHECK (price > 0),
    currency text NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    effective_from date NOT NULL,
    UNIQUE (tenant_id, recipe_version_id, branch_id, effective_from),
    CONSTRAINT menu_item_branch_prices_version_fk
        FOREIGN KEY (recipe_version_id, tenant_id)
        REFERENCES menu_recipe_versions (id, tenant_id),
    CONSTRAINT menu_item_branch_prices_branch_fk
        FOREIGN KEY (branch_id, tenant_id)
        REFERENCES platform_branches (id, tenant_id)
);

GRANT SELECT, INSERT ON menu_item_branch_prices TO gastroledger_app;

ALTER TABLE menu_item_branch_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_item_branch_prices FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS menu_item_branch_prices_scope ON menu_item_branch_prices;
CREATE POLICY menu_item_branch_prices_scope ON menu_item_branch_prices
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
