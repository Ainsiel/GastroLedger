\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS menu_recipes (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    code text NOT NULL,
    name text NOT NULL,
    recipe_type text NOT NULL CHECK (recipe_type IN ('sub_recipe', 'menu_item')),
    UNIQUE (tenant_id, code),
    UNIQUE (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS menu_recipe_versions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    recipe_id uuid NOT NULL,
    version text NOT NULL,
    yield_quantity numeric(24, 10) NOT NULL CHECK (yield_quantity > 0),
    yield_unit_id uuid NOT NULL,
    effective_from date NOT NULL,
    status text NOT NULL CHECK (status IN ('approved', 'scheduled')),
    approved_at timestamptz NOT NULL,
    UNIQUE (tenant_id, recipe_id, version),
    UNIQUE (id, tenant_id),
    CONSTRAINT menu_recipe_versions_recipe_fk
        FOREIGN KEY (recipe_id, tenant_id)
        REFERENCES menu_recipes (id, tenant_id),
    CONSTRAINT menu_recipe_versions_yield_unit_fk
        FOREIGN KEY (yield_unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS menu_recipe_components (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    recipe_version_id uuid NOT NULL,
    component_type text NOT NULL CHECK (component_type IN ('ingredient', 'sub_recipe')),
    ingredient_id uuid,
    component_recipe_id uuid,
    quantity numeric(24, 10) NOT NULL CHECK (quantity > 0),
    unit_id uuid NOT NULL,
    CHECK (
        (component_type = 'ingredient' AND ingredient_id IS NOT NULL AND component_recipe_id IS NULL)
        OR
        (component_type = 'sub_recipe' AND ingredient_id IS NULL AND component_recipe_id IS NOT NULL)
    ),
    CONSTRAINT menu_recipe_components_version_fk
        FOREIGN KEY (recipe_version_id, tenant_id)
        REFERENCES menu_recipe_versions (id, tenant_id),
    CONSTRAINT menu_recipe_components_ingredient_fk
        FOREIGN KEY (ingredient_id, tenant_id)
        REFERENCES menu_ingredients (id, tenant_id),
    CONSTRAINT menu_recipe_components_recipe_fk
        FOREIGN KEY (component_recipe_id, tenant_id)
        REFERENCES menu_recipes (id, tenant_id),
    CONSTRAINT menu_recipe_components_unit_fk
        FOREIGN KEY (unit_id, tenant_id)
        REFERENCES menu_units (id, tenant_id)
);

CREATE TABLE IF NOT EXISTS menu_cost_snapshots (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES platform_tenants(id),
    recipe_version_id uuid NOT NULL,
    as_of date NOT NULL,
    total_cost numeric(24, 10) NOT NULL CHECK (total_cost >= 0),
    status text NOT NULL CHECK (status IN ('current', 'missing_cost')),
    UNIQUE (tenant_id, recipe_version_id),
    CONSTRAINT menu_cost_snapshots_version_fk
        FOREIGN KEY (recipe_version_id, tenant_id)
        REFERENCES menu_recipe_versions (id, tenant_id)
);

GRANT SELECT, INSERT ON
    menu_recipes,
    menu_recipe_versions,
    menu_recipe_components,
    menu_cost_snapshots
TO gastroledger_app;

ALTER TABLE menu_recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_recipes FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_recipe_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_recipe_versions FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_recipe_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_recipe_components FORCE ROW LEVEL SECURITY;
ALTER TABLE menu_cost_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE menu_cost_snapshots FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS menu_recipes_scope ON menu_recipes;
CREATE POLICY menu_recipes_scope ON menu_recipes
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS menu_recipe_versions_scope ON menu_recipe_versions;
CREATE POLICY menu_recipe_versions_scope ON menu_recipe_versions
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS menu_recipe_components_scope ON menu_recipe_components;
CREATE POLICY menu_recipe_components_scope ON menu_recipe_components
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

DROP POLICY IF EXISTS menu_cost_snapshots_scope ON menu_cost_snapshots;
CREATE POLICY menu_cost_snapshots_scope ON menu_cost_snapshots
USING (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant_id', true), '')::uuid);

COMMIT;
