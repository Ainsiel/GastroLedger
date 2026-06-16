\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS menu_units (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    code text NOT NULL,
    name text NOT NULL,
    dimension text NOT NULL CHECK (dimension IN ('mass', 'volume', 'count')),
    UNIQUE (tenant_id, code),
    UNIQUE (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS menu_conversion_factors (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    source_unit_id uuid NOT NULL,
    target_unit_id uuid NOT NULL,
    factor numeric(24, 10) NOT NULL CHECK (factor > 0),
    effective_from date NOT NULL,
    UNIQUE (tenant_id, source_unit_id, target_unit_id, effective_from),
    CHECK (source_unit_id <> target_unit_id),
    CONSTRAINT menu_conversion_source_unit_fk
        FOREIGN KEY (source_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id),
    CONSTRAINT menu_conversion_target_unit_fk
        FOREIGN KEY (target_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS menu_ingredients (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    code text NOT NULL,
    name text NOT NULL,
    purchase_unit_id uuid NOT NULL,
    consumption_unit_id uuid NOT NULL,
    shelf_life_days integer NOT NULL CHECK (shelf_life_days BETWEEN 1 AND 3650),
    critical_stock_quantity numeric(24, 10) NOT NULL CHECK (critical_stock_quantity > 0),
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    UNIQUE (tenant_id, code),
    UNIQUE (id, tenant_id),
    CONSTRAINT menu_ingredients_purchase_unit_fk
        FOREIGN KEY (purchase_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id),
    CONSTRAINT menu_ingredients_consumption_unit_fk
        FOREIGN KEY (consumption_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id)
);

GRANT SELECT, INSERT, UPDATE ON
    menu_units,
    menu_conversion_factors,
    menu_ingredients
TO gastroledger_app;

ALTER TABLE menu_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_units FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_conversion_factors ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_conversion_factors FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_ingredients FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS menu_units_scope ON menu_units;
CREATE POLICY menu_units_scope ON menu_units
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS menu_conversion_factors_scope ON menu_conversion_factors;
CREATE POLICY menu_conversion_factors_scope ON menu_conversion_factors
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS menu_ingredients_scope ON menu_ingredients;
CREATE POLICY menu_ingredients_scope ON menu_ingredients
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
